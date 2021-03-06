# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import pytest
import pexpect
import os

from tests.common.custom_cluster_test_suite import CustomClusterTestSuite

SHELL_CMD = "%s/bin/impala-shell.sh" % os.environ['IMPALA_HOME']


class TestShellInteractive(CustomClusterTestSuite):

  @pytest.mark.execute_serially
  @CustomClusterTestSuite.with_args(impalad_args="-default_pool_max_requests 1")
  def test_admission_status(self):
    """Test whether the admission status gets printed if a query gets queued when
    either live_summary or live_progress is set to true"""
    expected_admission_status = "Query queued. Latest queuing reason: " \
                                "number of running queries 1 is at or over limit 1"
    # Start a long running query so that the next one gets queued.
    sleep_query_handle = self.client.execute_async("select sleep(10000)")
    self.client.wait_for_admission_control(sleep_query_handle)
    proc = pexpect.spawn(' '.join([SHELL_CMD, "-i localhost:21000"]))
    # Check with only live_summary set to true.
    proc.expect("21000] default>")
    proc.sendline("set live_summary=true;")
    proc.sendline("select 1;")
    proc.expect(expected_admission_status)
    proc.sendcontrol('c')
    proc.expect("Cancelling Query")
    # Check with only live_progress set to true.
    proc.sendline("set live_summary=false;")
    proc.sendline("set live_progress=true;")
    proc.sendline("select 1;")
    proc.expect(expected_admission_status)
