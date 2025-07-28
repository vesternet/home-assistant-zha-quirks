"""Vesternet VES-ZB-WAL-011 4 Button Wall Controller."""

from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zigpy.zcl import foundation
from typing import Optional, Union, Any
import zigpy.types as t
from zigpy.zcl.clusters.general import (
    Basic,
    Groups,
    Identify,
    LevelControl,
    OnOff,
    Ota,
    PowerConfiguration,
    Scenes,
)
from zigpy.zcl.clusters.homeautomation import Diagnostic
from zigpy.zcl.clusters.lighting import Color
from zigpy.zcl.clusters.lightlink import LightLink

from zhaquirks.const import (
    CLUSTER_ID,
    COMMAND,
    COMMAND_MOVE,
    COMMAND_MOVE_ON_OFF,
    COMMAND_OFF,
    COMMAND_ON,
    COMMAND_STOP,
    COMMAND_STOP_ON_OFF,
    DEVICE_TYPE,
    ENDPOINT_ID,
    ENDPOINTS,
    INPUT_CLUSTERS,
    LONG_PRESS,
    ALT_LONG_PRESS,
    LONG_RELEASE,
    ALT_LONG_RELEASE,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PARAMS,
    PROFILE_ID,
    SHORT_PRESS,
)

class VesternetSuppressDuplicateFrames(CustomCluster):
    """Vesternet suppress duplicate frames custom cluster."""

    def __init__(self, *args, **kwargs):
        """Init."""
        self.last_tsn = -1
        super().__init__(*args, **kwargs)

    def handle_message(
        self,
        hdr: foundation.ZCLHeader,
        args: list[Any],
        *,
        dst_addressing: Optional[
            Union[t.Addressing.Group, t.Addressing.IEEE, t.Addressing.NWK]
        ] = None,
    ) -> None:
        self.debug(
            "Received command 0x%02X (TSN %d): %s", hdr.command_id, hdr.tsn, args
        )
        if hdr.frame_control.is_cluster:
            if dst_addressing == t.Addressing.Group:
                self.debug("ignoring group message")
            elif hdr.tsn == self.last_tsn:
                self.debug("ignoring duplicate frame")
            else:
                self.debug("process this message")
                self.last_tsn = hdr.tsn 
                self.handle_cluster_request(hdr, args, dst_addressing=dst_addressing)
                self.listener_event("cluster_command", hdr.tsn, hdr.command_id, args)
                return
        self.listener_event("general_command", hdr, args)
        self.handle_cluster_general_request(hdr, args, dst_addressing=dst_addressing)    

class VesternetOnOffCommandCluster(OnOff, VesternetSuppressDuplicateFrames):
    """Vesternet On Off cluster that suppresses duplicate frames."""

class VesternetLevelControlCommandCluster(LevelControl, VesternetSuppressDuplicateFrames):
    """Vesternet Level Control cluster that suppresses duplicate frames."""

class VesternetScenesCommandCluster(Scenes, VesternetSuppressDuplicateFrames):
    """Vesternet Scenes cluster that suppresses duplicate frames."""

class VesternetVESZBWAL0114ButtonWallController(CustomDevice):
    """Vesternet VES-ZB-WAL-011 4 Button Wall Controller."""

    signature = {
        MODELS_INFO: [("Sunricher", "ZG2833K4_EU06")],
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.LEVEL_CONTROL_SWITCH,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                    Diagnostic.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
                    Ota.cluster_id,
                    Color.cluster_id,
                    LightLink.cluster_id,
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.LEVEL_CONTROL_SWITCH,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                    Diagnostic.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
                    Ota.cluster_id,
                    Color.cluster_id,
                    LightLink.cluster_id,
                ],
            }
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.LEVEL_CONTROL_SWITCH,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    PowerConfiguration.cluster_id,
                    Diagnostic.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    VesternetOnOffCommandCluster,
                    VesternetLevelControlCommandCluster,
                    Ota.cluster_id,
                    Color.cluster_id,
                    LightLink.cluster_id,
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.LEVEL_CONTROL_SWITCH,
                INPUT_CLUSTERS: [ ],
                OUTPUT_CLUSTERS: [
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    VesternetOnOffCommandCluster,
                    VesternetLevelControlCommandCluster,
                    Color.cluster_id,
                    LightLink.cluster_id,
                ],
            }
        }
    }

    device_automation_triggers = {
        (SHORT_PRESS, "Group 1 On"): {
            COMMAND: COMMAND_ON,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 6,
        },
        (LONG_PRESS, "Group 1 On"): {
            COMMAND: COMMAND_MOVE_ON_OFF,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 0, "rate": 50},
        },
        (ALT_LONG_PRESS, "Group 1 On"): {
            COMMAND: COMMAND_MOVE,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 0, "rate": 50},
        },
        (ALT_LONG_RELEASE, "Group 1"): {
            COMMAND: COMMAND_STOP,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 8,
        },
        (LONG_RELEASE, "Group 1"): {
            COMMAND: COMMAND_STOP_ON_OFF,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 8,
        },
        (SHORT_PRESS, "Group 1 Off"): {
            COMMAND: COMMAND_OFF,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 6,
        },
        (LONG_PRESS, "Group 1 Off"): {
            COMMAND: COMMAND_MOVE_ON_OFF,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 1, "rate": 50},
        },
        (ALT_LONG_PRESS, "Group 1 Off"): {
            COMMAND: COMMAND_MOVE,
            ENDPOINT_ID: 1,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 1, "rate": 50, "options_mask": 0, "options_override": 0},
        },
        (SHORT_PRESS, "Group 2 On"): {
            COMMAND: COMMAND_ON,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 6,
        },
        (LONG_PRESS, "Group 2 On"): {
            COMMAND: COMMAND_MOVE_ON_OFF,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 0, "rate": 50},
        },
        (ALT_LONG_PRESS, "Group 2 On"): {
            COMMAND: COMMAND_MOVE,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 0, "rate": 50},
        },
        (ALT_LONG_RELEASE, "Group 2"): {
            COMMAND: COMMAND_STOP,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 8,
        },
        (LONG_RELEASE, "Group 2"): {
            COMMAND: COMMAND_STOP_ON_OFF,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 8,
        },
        (SHORT_PRESS, "Group 2 Off"): {
            COMMAND: COMMAND_OFF,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 6,
        },
        (LONG_PRESS, "Group 2 Off"): {
            COMMAND: COMMAND_MOVE_ON_OFF,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 1, "rate": 50},
        },
        (ALT_LONG_PRESS, "Group 2 Off"): {
            COMMAND: COMMAND_MOVE,
            ENDPOINT_ID: 2,
            CLUSTER_ID: 8,
            PARAMS: {"move_mode": 1, "rate": 50, "options_mask": 0, "options_override": 0},
        },
    }