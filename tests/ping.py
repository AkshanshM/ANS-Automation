"""
INTEL CONFIDENTIAL
Copyright 2024 - 2024 Intel Corporation All Rights Reserved.
The source code contained or described herein and all documents related to the
source code ("Material") are owned by Intel Corporation or its suppliers or
licensors. Title to the Material remains with Intel Corporation or its
suppliers and licensors. The Material contains trade secrets and proprietary
and confidential information of Intel or its suppliers and licensors.
The Material is protected by worldwide copyright and trade secret laws and
treaty provisions. No part of the Material may be used, copied, reproduced,
modified, published, uploaded, posted, transmitted, distributed, or disclosed
in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.

Created on 22/02/2024
@author: akshan1x

Test contents:
    Basic ping test between SUT and Client.

Test steps:
    1. Run ping from SUT adapter to client adapter for 4 seconds

Pass criteria:
    1. The SUT adapter is able to contact the client adapter

Fail criteria:
    1. The SUT adapter is not able to contact the client adapter

User parameters:
    ip_ver: Use IPv4 or IPv6
    type ip_ver: "4" or "6"

Default configuration:
    The test will run with ipv4, then again with ipv6.

"""

from libs.basetests.basetest import BaseTest
from libs import log_fail, log_pass, log_info
from libs.utils import string_to_bool

log_name = __name__


class PingTest(BaseTest):
    """Simple Ping AGAT test-case"""

    supported_oses = ("ESXI", "FREEBSD", "HYPERV", "KVM", "LINUX", "WINDOWS")
    default_conf = [{"ip_ver": "4"}, {"ip_ver": "6"}]
    name = "PING TEST"

    def _validate_ping_time(self, ping_output, time_threshold):
        """Validate ping time based on a time_treshold

        :param ping_output: ping output
        :type ping_output: str
        :param time_threshold: ping max time
        :type time_threshold: float
        """
        self.log_step("Validate ping time.")
        if ping_output.rtt_max > float(time_threshold):
            log_fail("Allowed time {0} has been exceeded.".format(time_threshold))
        else:
            log_pass("Ping Performance passed.")

    def run(
        self, ip_ver="4", validate_performance=False, ping_count=4, time_treshold=2, **kwargs
    ):  # pylint: disable=unused-argument
        validate_performance = string_to_bool(validate_performance)
        ping_count = int(ping_count)

        for sut_adapter, client_adapter in zip(self.sut_adapters, self.client_adapters):
            log_info("Tested adapter: %s " % sut_adapter)
            log_info("Client adapter: %s" % client_adapter)
            self.log_step("Ping from SUT to Client {0} times.".format(ping_count))
            out, rc = self.sut_host.ping(client_adapter.tested_ip, source=sut_adapter.tested_ip, count=ping_count)
            if rc != 0:
                log_fail("Cannot communicate with client")
            else:
                log_pass("Client contacted")

                # validate_performance tested only on Linux and Windows
                if validate_performance:
                    self._validate_ping_time(out, time_treshold)
                    self.log_step("Ping from Client to SUT {0} times.".format(ping_count))
                    out, rc = self.client_host.ping(
                        sut_adapter.tested_ip, source=client_adapter.tested_ip, count=ping_count
                    )
                    if rc != 0:
                        log_fail("Cannot communicate with SUT")
                    else:
                        log_pass("SUT contacted")
                        self._validate_ping_time(out, time_treshold)