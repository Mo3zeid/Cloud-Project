"""OpenNebula service — wraps pyone / XML-RPC calls."""

import logging
import random

logger = logging.getLogger(__name__)


class OpenNebulaService:
    """Interface to the OpenNebula cloud controller."""

    def __init__(self, config):
        self.config = config
        self.demo_mode = config.get("DEMO_MODE", True)
        self.rpc_url = config.get("ONE_RPC_URL", "http://localhost:2633/RPC2")
        self.session = "{}:{}".format(
            config.get("ONE_USERNAME", "oneadmin"),
            config.get("ONE_PASSWORD", "oneadmin"),
        )
        self.network_id = config.get("ONE_NETWORK_ID", 0)
        self._server = None

    # ── Connection ───────────────────────────────────────────────────

    def connect(self):
        """Initialise pyone connection (or XML-RPC fallback)."""
        if self.demo_mode:
            logger.info("[DEMO] OpenNebula connection simulated.")
            return

        try:
            import pyone
            self._server = pyone.OneServer(self.rpc_url, session=self.session)
            self.is_pyone = True
            logger.info(f"Connected to OpenNebula at {self.rpc_url}")
        except ImportError:
            logger.warning("pyone not installed — falling back to xmlrpc.client")
            import xmlrpc.client
            self._server = xmlrpc.client.ServerProxy(self.rpc_url)
            self.is_pyone = False
        except Exception as e:
            logger.error(f"Failed to connect to OpenNebula: {e}")
            raise

    # ── VM Lifecycle ─────────────────────────────────────────────────

    def create_vm(self, os_image, cpu, ram, storage, gpu, software_stack, vm_name):
        """
        Provision a new VM through OpenNebula.
        
        Returns the VM ID (int).
        """
        if self.demo_mode:
            vm_id = random.randint(100, 9999)
            logger.info(f"[DEMO] Simulated VM creation: {vm_name} → VM ID {vm_id}")
            return vm_id

        self.connect()

        # The os_image parameter is either the string representation of the image ID or a config key
        try:
            image_id = int(os_image)
        except ValueError:
            images = self.list_images()
            image_id = images.get(os_image, {}).get("image_id", 0)

        # Build template string
        gpu_section = ""
        if gpu:
            gpu_section = """
PCI = [
    CLASS = "0300",
    DEVICE = "",
    SHORT_ADDRESS = "",
    TYPE = "GPU",
    VENDOR = ""
]"""

        template = f"""
NAME = "{vm_name}"
CPU  = "0.2"
VCPU = "{cpu}"
MEMORY = "{ram}"
DISK = [
    IMAGE_ID = "{image_id}",
    SIZE = "{storage * 1024}"
]
NIC = [
    NETWORK_ID = "{self.network_id}"
]
GRAPHICS = [
    LISTEN = "0.0.0.0",
    TYPE = "VNC"
]
CONTEXT = [
    NETWORK = "YES",
    SSH_PUBLIC_KEY = "$USER[SSH_PUBLIC_KEY]",
    PASSWORD = "research123",
    SET_HOSTNAME = "$NAME",
    SOFTWARE_STACK = "{software_stack}"
]{gpu_section}
OS = [
    ARCH = "x86_64",
    BOOT = "disk0"
]
"""
        try:
            # Try pyone-style call first
            if self.is_pyone:
                # Allocate template then instantiate
                template_id = self._server.template.allocate(template)
                vm_id = self._server.template.instantiate(template_id, vm_name)
                logger.info(f"VM {vm_name} created with ID {vm_id}")
                return vm_id
            else:
                # Raw XML-RPC
                result = self._server.one.template.allocate(self.session, template)
                if result[0]:
                    template_id = result[1]
                    result2 = self._server.one.template.instantiate(
                        self.session, template_id, vm_name, False, ""
                    )
                    if result2[0]:
                        vm_id = result2[1]
                        logger.info(f"VM {vm_name} created with ID {vm_id}")
                        return vm_id
                    else:
                        raise RuntimeError(f"VM instantiate failed: {result2[1]}")
                else:
                    raise RuntimeError(f"Template allocate failed: {result[1]}")
        except Exception as e:
            logger.error(f"VM creation failed: {e}")
            raise

    def get_vm_status(self, vm_id):
        """
        Query VM state.
        
        Returns dict with 'state', 'lcm_state', 'state_name'.
        
        OpenNebula states:
            0=INIT, 1=PENDING, 2=HOLD, 3=ACTIVE,
            4=STOPPED, 5=SUSPENDED, 6=DONE, 8=POWEROFF, 9=UNDEPLOYED
        LCM states (when ACTIVE):
            3=RUNNING, 5=MIGRATE, 12=UNKNOWN, etc.
        """
        if self.demo_mode:
            return {"state": 3, "lcm_state": 3, "state_name": "RUNNING"}

        self.connect()

        state_names = {
            0: "INIT", 1: "PENDING", 2: "HOLD", 3: "ACTIVE",
            4: "STOPPED", 5: "SUSPENDED", 6: "DONE",
            8: "POWEROFF", 9: "UNDEPLOYED",
        }

        try:
            if self.is_pyone:
                vm_info = self._server.vm.info(vm_id)
                state = int(vm_info.STATE)
                lcm_state = int(vm_info.LCM_STATE)
            else:
                result = self._server.one.vm.info(self.session, vm_id)
                if result[0]:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(result[1])
                    state = int(root.find("STATE").text)
                    lcm_state = int(root.find("LCM_STATE").text)
                else:
                    raise RuntimeError(f"VM info failed: {result[1]}")

            return {
                "state": state,
                "lcm_state": lcm_state,
                "state_name": state_names.get(state, "UNKNOWN"),
            }
        except Exception as e:
            logger.error(f"Failed to get VM {vm_id} status: {e}")
            raise

    def get_vm_ip(self, vm_id):
        """Extract IP address from VM info."""
        if self.demo_mode:
            return f"192.168.122.{random.randint(10, 250)}"

        self.connect()

        try:
            if self.is_pyone:
                vm_info = self._server.vm.info(vm_id)
                # Navigate template → NIC → IP
                template = vm_info.TEMPLATE
                if isinstance(template, dict) and "NIC" in template:
                    nic = template["NIC"]
                    if isinstance(nic, list):
                        return nic[0].get("IP", "N/A")
                    return nic.get("IP", "N/A")
                elif hasattr(template, 'NIC'):
                    nic = template.NIC
                    if isinstance(nic, list):
                        return nic[0].get("IP", "N/A") if hasattr(nic[0], 'get') else getattr(nic[0], 'IP', 'N/A')
                    return nic.get("IP", "N/A") if hasattr(nic, 'get') else getattr(nic, 'IP', 'N/A')
                return "N/A"
            else:
                result = self._server.one.vm.info(self.session, vm_id)
                if result[0]:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(result[1])
                    ip_elem = root.find(".//NIC/IP")
                    return ip_elem.text if ip_elem is not None else "N/A"
                return "N/A"
        except Exception as e:
            logger.error(f"Failed to get VM {vm_id} IP: {e}")
            return "N/A"

    def terminate_vm(self, vm_id):
        """Terminate and delete a VM."""
        if self.demo_mode:
            logger.info(f"[DEMO] Simulated VM termination: VM ID {vm_id}")
            return True

        self.connect()

        try:
            if self.is_pyone:
                self._server.vm.action("terminate-hard", vm_id)
            else:
                self._server.one.vm.action(self.session, "terminate-hard", vm_id)
            logger.info(f"VM {vm_id} terminated.")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate VM {vm_id}: {e}")
            raise

    # ── Information Queries ──────────────────────────────────────────

    def list_images(self):
        """List available OS images from OpenNebula."""
        if self.demo_mode:
            return self.config.get("OS_IMAGES", {})

        self.connect()

        try:
            images = {}
            if self.is_pyone:
                pool = self._server.imagepool.info(-2, -1, -1)
                for img in pool.IMAGE:
                    images[str(img.ID)] = {
                        "name": img.NAME,
                        "image_id": img.ID,
                        "icon": "💿",
                        "description": f"OpenNebula Image ID {img.ID}",
                    }
                return images
            else:
                result = self._server.one.imagepool.info(self.session, -2, -1, -1)
                if result[0]:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(result[1])
                    for img in root.findall('IMAGE'):
                        img_id = int(img.find('ID').text)
                        img_name = img.find('NAME').text
                        images[str(img_id)] = {
                            "name": img_name,
                            "image_id": img_id,
                            "icon": "💿",
                            "description": f"OpenNebula Image ID {img_id}",
                        }
                return images
        except Exception as e:
            logger.error(f"Failed to list images: {e}")
            return {}

    def get_version(self):
        """Get OpenNebula version — useful for health checks."""
        if self.demo_mode:
            return "6.8.0 (Demo Mode)"

        self.connect()

        try:
            if self.is_pyone:
                return self._server.system.version()
            else:
                result = self._server.one.system.version(self.session)
                if result[0]:
                    return result[1]
                return "Unknown"
        except Exception as e:
            logger.error(f"Failed to get version: {e}")
            return "Unavailable"
