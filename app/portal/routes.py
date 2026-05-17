"""Portal routes — dashboard, job creation, job monitoring."""

import os
import uuid
from datetime import datetime
from flask import (
    render_template, redirect, url_for, flash,
    request, current_app, send_from_directory, jsonify,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.portal import portal_bp
from app.extensions import db
from app.models import Job
from app.services.opennebula_service import OpenNebulaService


@portal_bp.route("/")
def index():
    """Landing page — redirect to dashboard if logged in."""
    if current_user.is_authenticated:
        return redirect(url_for("portal.dashboard"))
    return redirect(url_for("auth.login"))


@portal_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard with job overview."""
    jobs = current_user.jobs.all()
    stats = {
        "total": len(jobs),
        "running": sum(1 for j in jobs if j.status in ("running", "provisioning")),
        "completed": sum(1 for j in jobs if j.status == "completed"),
        "failed": sum(1 for j in jobs if j.status == "failed"),
    }
    from app.services.opennebula_service import OpenNebulaService
    os_images = OpenNebulaService(current_app.config).list_images()

    return render_template("portal/dashboard.html", jobs=jobs, stats=stats, os_images=os_images)


@portal_bp.route("/new-job")
@login_required
def new_job():
    """Multi-step form for creating a new compute job."""
    os_images = OpenNebulaService(current_app.config).list_images()
    cpu_options = current_app.config["CPU_OPTIONS"]
    ram_options = current_app.config["RAM_OPTIONS"]
    software_stacks = current_app.config["SOFTWARE_STACKS"]
    return render_template(
        "portal/new_job.html",
        os_images=os_images,
        cpu_options=cpu_options,
        ram_options=ram_options,
        software_stacks=software_stacks,
    )


@portal_bp.route("/submit-job", methods=["POST"])
@login_required
def submit_job():
    """Validate and create a new compute job."""
    os_image = request.form.get("os_image", "")
    cpu = request.form.get("cpu", "1")
    ram = request.form.get("ram", "1024")
    storage = request.form.get("storage", "10")
    gpu = request.form.get("gpu") == "on"
    software_stack = request.form.get("software_stack", "")

    # Validate selections
    os_images = OpenNebulaService(current_app.config).list_images()
    valid_os = list(os_images.keys())
    valid_stacks = list(current_app.config["SOFTWARE_STACKS"].keys())
    valid_cpus = current_app.config["CPU_OPTIONS"]
    valid_rams = [r["value"] for r in current_app.config["RAM_OPTIONS"]]
    valid_storage = [s["value"] for s in current_app.config["STORAGE_OPTIONS"]]

    errors = []
    if os_image not in valid_os:
        errors.append("Invalid operating system selection.")
    if int(cpu) not in valid_cpus:
        errors.append("Invalid CPU selection.")
    if int(ram) not in valid_rams:
        errors.append("Invalid RAM selection.")
    if int(storage) not in valid_storage:
        errors.append("Invalid storage selection.")
    if software_stack not in valid_stacks:
        errors.append("Invalid software stack selection.")

    # Handle file upload
    dataset_filename = None
    dataset_path = None
    file = request.files.get("dataset")
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        dataset_path = os.path.join(upload_dir, unique_name)
        file.save(dataset_path)
        dataset_filename = filename

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("portal.new_job"))

    # Create job
    os_info = os_images.get(os_image, {})
    stack_info = current_app.config["SOFTWARE_STACKS"][software_stack]
    vm_name = f"research-{current_user.username}-{uuid.uuid4().hex[:8]}"

    job = Job(
        user_id=current_user.id,
        vm_name=vm_name,
        os_image=os_image,
        cpu=int(cpu),
        ram=int(ram),
        storage=int(storage),
        gpu=gpu,
        software_stack=software_stack,
        dataset_filename=dataset_filename,
        dataset_path=dataset_path,
        status="pending",
    )
    db.session.add(job)
    db.session.commit()

    flash(f"Job #{job.id} created! Provisioning will begin shortly.", "success")
    return redirect(url_for("portal.job_detail", job_id=job.id))


@portal_bp.route("/job/<int:job_id>")
@login_required
def job_detail(job_id):
    """Job detail page."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    os_images = OpenNebulaService(current_app.config).list_images()
    software_stacks = current_app.config["SOFTWARE_STACKS"]
    return render_template(
        "portal/job_detail.html",
        job=job,
        os_images=os_images,
        software_stacks=software_stacks,
    )


@portal_bp.route("/job/<int:job_id>/status")
@login_required
def job_status(job_id):
    """AJAX endpoint for real-time job status polling."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    return jsonify({
        "id": job.id,
        "status": job.status,
        "status_icon": job.status_icon,
        "status_color": job.status_color,
        "vm_id": job.vm_id,
        "vm_ip": job.vm_ip,
        "error_message": job.error_message,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    })


@portal_bp.route("/job/<int:job_id>/download")
@login_required
def download_result(job_id):
    """Download completed job results."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    if job.status != "completed" or not job.result_path:
        flash("Results are not available yet.", "error")
        return redirect(url_for("portal.job_detail", job_id=job.id))

    directory = os.path.dirname(job.result_path)
    filename = os.path.basename(job.result_path)
    return send_from_directory(directory, filename, as_attachment=True)


@portal_bp.route("/job/<int:job_id>/terminate", methods=["POST"])
@login_required
def terminate_job(job_id):
    """Terminate a running job."""
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()

    if job.status in ("pending", "provisioning", "running"):
        job.status = "failed"
        job.error_message = "Terminated by user."
        job.completed_at = datetime.utcnow()
        db.session.commit()

        # Attempt to terminate VM in OpenNebula
        if job.vm_id:
            try:
                from app.services.opennebula_service import OpenNebulaService
                one_service = OpenNebulaService(current_app.config)
                one_service.terminate_vm(job.vm_id)
            except Exception as e:
                current_app.logger.error(f"Failed to terminate VM {job.vm_id}: {e}")

        flash(f"Job #{job.id} has been terminated.", "info")
    else:
        flash("This job cannot be terminated.", "error")

    return redirect(url_for("portal.job_detail", job_id=job.id))
