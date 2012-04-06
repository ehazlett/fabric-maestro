#!/usr/bin/env python
#    Copyright 2012 Maestro Project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import unittest
import sys
# adjust path to find maestro
sys.path.append('../')
from fabric.api import env
from libcloud.compute.drivers.ec2 import EC2NodeDriver
from maestro.utils import get_provider_driver, load_env_keys

class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_get_ec2_provider_driver(self):
        ec2 = EC2NodeDriver(None, None)
        drv = get_provider_driver('ec2')
        self.assertTrue(isinstance(ec2, drv))
            
    def test_load_env_keys(self):
        load_env_keys()
        self.assertTrue(env.has_key('provider_keys'))
        self.assertTrue(env.get('provider_keys').has_key('ec2'))
