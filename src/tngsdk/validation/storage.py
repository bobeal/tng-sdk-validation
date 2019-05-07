#  Copyright (c) 2015 SONATA-NFV, UBIWHERE
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, UBIWHERE
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).

import os
import logging
import networkx as nx
import validators
import requests
from collections import Counter
from collections import OrderedDict
# importing the local event module, fix this ASAP
# from .event import *
# import util
from tngsdk.validation.util import descriptor_id, read_descriptor_file
# from util import read_descriptor_file, descriptor_id
from tngsdk.validation import event


log = logging.getLogger(__name__)
evtlog = event.get_logger('validator.events')


class DescriptorStorage(object):

    def __init__(self):
        """
        Initialize an object to store descriptors.
        """
        # dictionaries for services, functions and units
        self._packages = {}
        self._services = {}
        self._functions = {}
        self._units = {}
        self._tests = {}
        self._slices = {}
        self._slas = {}
        self._runtime_policies = {}

    @property
    def packages(self):
        """
        Provides the stored packages.
        :return: dictionary of packages.
        """
        return self._packages

    @property
    def services(self):
        """
        Provides the stored services.
        :return: dictionary of services.
        """
        return self._services

    @property
    def functions(self):
        """
        Provides the stored functions.
        :return: dictionary of functions.
        """
        return self._functions
    @property
    def tests(self):
        """
        Provides the stored tests
        :return: dictionary of tests
        """
        return self._tests
    @property
    def slices(self):
        """
        Provides the stored slices
        :return: dictionary of slices
        """
        return self._slices

    def create_package(self, descriptor_file):
        """
        Create and store a package based on the provided descriptor filename.
        If a package is already stored with the same id, it will return the
        stored package.
        :param descriptor_file: package descriptor filename
        :return: created package object or, if id exists, the stored package.
        """
        if not os.path.isfile(descriptor_file):
            return
        new_package = Package(descriptor_file)
        if new_package.id in self._packages:
            return self._packages[new_package.id]

        self._packages[new_package.id] = new_package
        return new_package

    def service(self, sid):
        """
        Obtain the service for the provided service id
        :param sid: service id
        :return: service descriptor object
        """
        if sid not in self.services:
            log.error("Service id='{0}' is not stored.".format(sid))
            return
        return self.services[sid]
    def create_service(self, descriptor_file):
        """
        Create and store a service based on the provided descriptor filename.
        If a service is already stored with the same id, it will return the
        stored service.
        :param descriptor_file: service descriptor filename
        :return: created service object or, if id exists, the stored service.
        """
        if not os.path.isfile(descriptor_file):
            return
        new_service = Service(descriptor_file)
        if not new_service.content or not new_service.id:
            return

        if new_service.id in self._services:
            return self._services[new_service.id]

        self._services[new_service.id] = new_service
        return new_service

    def function(self, fid):
        """
        Obtain the function for the provided function id
        :param fid: function id
        :return: function descriptor object
        """
        if fid not in self._functions[fid]:
            log.error("Function descriptor id='{0}' is not stored.".format(fid))
            return
        return self.functions[fid]
    def create_function(self, descriptor_file):
        """
        Create and store a function based on the provided descriptor filename.
        If a function is already stored with the same id, it will return the
        stored function.
        :param descriptor_file: function descriptor filename
        :return: created function object or, if id exists, the stored function.
        """
        if not os.path.isfile(descriptor_file):
            return
        new_function = Function(descriptor_file)
        if new_function.id in self._functions.keys():
            return self._functions[new_function.id]
        self._functions[new_function.id] = new_function
        return new_function

    def test(self, tid):
        """
        Obtain the test for the provided test id
        :param tid: test id
        :return: test descriptor object
        """
        if tid not in self._tests[tid]:
            log.error("Test descriptor id='{0}' is not stored.".format(fid))
            return
        return self.tests[tid]
    def create_test(self, descriptor_file):
        """
        Create and store a test based on the provided descriptor filename.
        If a test is already stored with the same id, it will return the
        stored test.
        :param descriptor_file: test descriptor filename
        :return: created test object or, if id exists, the stored test.
        """
        if not os.path.isfile(descriptor_file):
            return
        new_test = Test(descriptor_file)
        if not new_test.content:
            return
        content = new_test.content
        new_test.name = content["name"]

        if new_test.id in self._tests.keys():
            return self._tests[new_test.id]

        self._tests[new_test.id] = new_test
        return new_test

    def slice(self, sid):
        """
        Obtain the slice for the provided slice id
        :param tid: test id
        :return: test descriptor object
        """
        if sid not in self._slices[sid]:
            log.error("Slice descriptor id='{0}' is not stored.".format(sid))
            return
        return self.slices[sid]
    def create_slice(self, descriptor_file):
        """
        Create and store a slice based on the provided descriptor filename.
        If a slice is already stored with the same id, it will return the
        stored slice.
        :param descriptor_file: slice descriptor filename
        :return: created slice object or, if id exists, the stored slice.
        """
        if not os.path.isfile(descriptor_file):
            return
        new_slice = Slice(descriptor_file)
        if not new_slice.content:
            return
        content = new_slice.content
        new_slice.name = content["name"]

        if new_slice.id in self._slices.keys():
            return self._slices[new_slice.id]

        self._slices[new_slice.id] = new_slice
        return new_slice

    def sla(self, sla_id):
        """
        Obtain the sla for the provided sla id
        :param sla_id: sla id
        :return: sla descriptor object
        """
        if sla_id not in self._slas[sla_id]:
            log.error("SLA descriptor id='{0}' is not stored.".format(sla_id))
            return
        return self.slas[sla_id]
    def create_sla(self, descriptor_file):
        """
        Create and store a sla based on the provided descriptor filename.
        If a sla is already stored with the same id, it will return the
        stored sla.
        :param descriptor_file: sla descriptor filename
        :return: created sla object or, if id exists, the stored sla.
        """
        if not os.path.isfile(descriptor_file):
            return
        new_sla = SLA(descriptor_file)
        if not new_sla.content:
            return
        content = new_sla.content
        new_sla.name = content["name"]

        if new_sla.id in self._slas.keys():
            return self._slas[new_sla.id]

        self._slas[new_sla.id] = new_sla
        return new_sla

    def runtime_policy(self, rpid):
        """
        Obtain the sla for the provided sla id
        :param rpid: rpid
        :return: rp descriptor object
        """
        if rpid not in self._runtime_policies[rpid]:
            log.error("RP descriptor id='{0}' is not stored.".format(rpid))
            return
        return self.runtime_policies[rpid]
    def create_runtime_policy(self, descriptor_file):
        """
        Create and store a rp based on the provided descriptor filename.
        If a rp is already stored with the same id, it will return the
        stored sla.
        :param descriptor_file: rp descriptor filename
        :return: created rp object or, if id exists, the stored rp.
        """
        if not os.path.isfile(descriptor_file):
            return
        new_runtime_policy = Runtime_Policy(descriptor_file)
        if not new_runtime_policy.content:
            return
        content = new_runtime_policy.content
        new_runtime_policy.name = content["name"]

        if new_runtime_policy.id in self._runtime_policies.keys():
            return self._runtime_policies[new_runtime_policy.id]

        self._runtime_policies[new_runtime_policy.id] = new_runtime_policy
        return new_runtime_policy

class Node:
    def __init__(self, nid):
        """
        Initialize a node object.
        A node holds multiple network connection points
        :param nid: node id
        """
        self._id = nid
        self._connection_points = []

    @property
    def id(self):
        """
        Identifier of the node.
        :return: node id
        """
        return self._id

    @property
    def connection_points(self):
        """
        Provides a list of interfaces associated with the node.
        :return: interface list
        """
        return self._connection_points

    @connection_points.setter
    def connection_points(self, value):
        self._connection_points = value

    def add_connection_point(self, cp):
        """
        Associate a new interface to the node.
        :param cp: connection point ID
        """
        if cp in self.connection_points:
            evtlog.log("Duplicate connection point",
                       "The CP id='{0}' is already stored in node "
                       "id='{1}'".format(cp, self.id),
                       self.id,
                       'evt_duplicate_cpoint')
            return

        # check if connection point has the correct format
        s_cp = cp.split(':')
        if len(s_cp) != 1:
            evtlog.log("Invalid_connection_point",
                       "The CP id='{0}' is invalid. The separator ':' is "
                       "reserved to reference connection points"
                       .format(cp),
                       self.id,
                       'evt_invalid_cpoint')
            return

        log.debug("Node id='{0}': adding connection point '{1}'"
                  .format(self.id, cp))

        self._connection_points.append(cp)

        return True


class VLink:
    def __init__(self, vl_id, cpr_u, cpr_v):
        """
        Initialize a vlink object.
        A vlink defines a connection between two connection_points.
        :param vl_id: link id
        :param cpr_u: connection point reference u
        :param cpr_v: connection point reference v
        """
        self._id = vl_id
        self._cpr_pair = [cpr_u, cpr_v]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{} -- {}".format(self.id, self.cpr_u, self.cpr_v)

    @property
    def id(self):
        return self._id

    @property
    def connection_point_refs(self):
        """
        The two connection points references composing the vlink
        in a list format [u, v]
        :return: list (size 2) of connection point references
        """
        return self._cpr_pair

    @property
    def cpr_u(self):
        """
        Connection point reference u
        """
        return self._cpr_pair[0]

    @property
    def cpr_v(self):
        """
        Connection point reference v
        """
        return self._cpr_pair[1]


class VBridge:
    def __init__(self, vb_id, cp_refs):
        """
        Initialize a vbridge object.
        A bridge contains a list of N associated connection point reference.
        """
        assert vb_id
        assert cp_refs

        self._id = vb_id
        self._cp_refs = cp_refs

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{}".format(self.connection_point_refs)

    @property
    def id(self):
        return self._id

    @property
    def connection_point_refs(self):
        return self._cp_refs
    @property
    def cp_refs(self):
        return self._cp_refs

class Descriptor(Node):
    def __init__(self, descriptor_file):
        """
        Initialize a generic descriptor object.
        This object inherits the node object.
        All descriptor objects contains the following properties:
            - id
            - content: descriptor dictionary
            - filename: filename of the descriptor
        :param descriptor_file: filename of the descriptor
        """
        self._id = None
        self._content = None
        self._filename = None
        self.filename = descriptor_file
        super().__init__(self.id)
        self._complete_graph = None
        self._graph = None
        self._vlinks = {}
        self._vbridges = {}

    @property
    def id(self):
        """
        Identification of descriptor
        :return: descriptor id
        """
        return self._id

    @property
    def content(self):
        """
        Descriptor dictionary.
        :return: descriptor dict
        """
        return self._content

    @content.setter
    def content(self, value):
        """
        Sets the descriptor dictionary.
        This modification will impact the id of the descriptor.
        :param value: descriptor dict
        """
        self._content = value
        self._id = descriptor_id(self._content)

    @property
    def filename(self):
        """
        Filename of the descriptor
        :return: descriptor filename
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        """
        Sets the descriptor filename.
        This modification will impact the content and id of the descriptor.
        :param value: descriptor filename
        """

        self._filename = value
        content = read_descriptor_file(self._filename)
        if content:
            self.content = content

    @property
    def vlinks(self):
        """
        Provides the links associated with the descriptor.
        :return: dictionary of link objects
        """
        return self._vlinks

    @property
    def vbridges(self):
        """
        Provides the bridges associated with the descriptor.
        :return: dictionary of vbridge objects
        """
        return self._vbridges

    @property
    def vlink_cp_refs(self):
        vlink_cps = []
        for vl_id, vl in self.vlinks.items():
            vlink_cps += vl.connection_point_refs
        return vlink_cps

    @property
    def vbridge_cp_refs(self):
        vbridge_cp_references = []
        for vb_id, vb in self.vbridges.items():
            vbridge_cp_references += vb.connection_point_refs
        return vbridge_cp_references

    @property
    def graph(self):
        """
        Network topology graph of the descriptor.
        :return: topology graph (networkx.Graph)
        """
        return self._graph

    @graph.setter
    def graph(self, value):
        """
        Sets the topology graph of the descriptor.
        :param value: topology graph (networkx.Graph)
        :return:
        """
        self._graph = value

    @property
    def complete_graph(self):
        return self._complete_graph

    @complete_graph.setter
    def complete_graph(self, value):
        self._complete_graph = value

    def load_connection_points(self):
        """
        Load connection points of the descriptor.
        It reads the section 'connection_points' of the descriptor contents.
        """

        if 'connection_points' not in self.content:
            return
        for cp in self.content['connection_points']:
            if not self.add_connection_point(cp['id']):
                return
        return True

    def add_vbridge(self, vb_id, cp_refs):
        """
        Add vbridge to the descriptor.
        """

        # check number of connection point references
        if len(cp_refs) < 1:
            evtlog.log("Bad number of connection points",
                       "The vlink id='{0}' must have at lease 1 connection "
                       "point reference"
                       .format(vb_id),
                       self.id,
                       'evt_invalid_vlink')
            return

        # check for duplicate virtual links
        if vb_id in self.vlinks.keys() or vb_id in self.vbridges.keys():
            evtlog.log("Duplicate virtual link",
                       "The vlink id='{0}' is already defined"
                       .format(vb_id),
                       self.id,
                       'evt_duplicate_vlink')
            return

        # check connection point reference format
        for cp in cp_refs:
            s_cp = cp.split(':')
            if len(s_cp) > 2:
                evtlog.log("Invalid connection point reference",
                           "The connection point reference '{0}' of vlink"
                           " id='{1}' has an incorrect format: found multiple "
                           "separators ':'"
                           .format(cp, vb_id),
                           self.id,
                           'evt_invalid_cpoint_ref')
                return

        self._vbridges[vb_id] = VBridge(vb_id, cp_refs)
        return True

    def add_vlink(self, vl_id, cp_refs):
        """
        Add vlink to the descriptor.
        """
        # check number of connection point references
        if len(cp_refs) != 2:
            evtlog.log("Bad number of connection points",
                       "The vlink id='{0}' must have exactly 2 connection "
                       "point references"
                       .format(vl_id),
                       self.id,
                       'evt_invalid_vlink')
            return

        # check for duplicate virtual links
        if vl_id in self.vlinks.keys() or vl_id in self.vbridges.keys():
            evtlog.log("Duplicate virtual link",
                       "The vlink id='{0}' is already defined"
                       .format(vl_id),
                       self.id,
                       'evt_duplicate_vlink')
            return

        # check connection point reference format
        for cp in cp_refs:
            s_cp = cp.split(':')
            if len(s_cp) > 2:
                evtlog.log("Invalid connection point reference",
                           "The connection point reference '{0}' of vlink"
                           " id='{1}' has an incorrect format: found multiple "
                           "separators ':'"
                           .format(cp, vl_id),
                           self.id,
                           'evt_invalid_cpoint_ref')
                return

        self._vlinks[vl_id] = VLink(vl_id, cp_refs[0], cp_refs[1])
        return True

    def load_virtual_links(self):
        """
        Load 'virtual_links' section of the descriptor.
        - 'e-line' virtual links will be stored in Link objects
        - 'e-lan' virtual links will be stored in Bridge objects
        - 'e-tree' virtual links will be stored in Bridge objects
        """
        if 'virtual_links' not in self.content:
            return
        for vl in self.content['virtual_links']:
            if not vl['id']:
                evtlog.log("Missing virtual link ID",
                           "A virtual link is missing its ID",
                           self.id,
                           'evt_invalid_vlink')
                return

            vl_type = vl['connectivity_type'].lower()
            if vl_type == 'e-line':
                if not self.add_vlink(vl['id'],
                                      vl['connection_points_reference']):
                    return

            if vl_type == 'e-lan':
                if not self.add_vbridge(vl['id'],
                                        vl['connection_points_reference']):
                    return

            if vl_type == 'e-tree':
                if not self.add_vbridge(vl['id'],
                                        vl['connection_points_reference']):
                    return

        return True

    def unused_connection_points(self):
        """
        Provides a list of connection points that are not referenced by
        'virtual_links'. Should only be invoked after connection points
        are loaded.
        """
        unused_cps = []
        for cp in self.connection_points:
            if cp not in self.vlink_cp_refs and \
                    cp not in self.vbridge_cp_refs:
                unused_cps.append(cp)
        return unused_cps

class Package(Descriptor):

    def __init__(self, descriptor_file):
        """
        Initialize a package object. This inherits the descriptor object.
        :param descriptor_file: descriptor filename
        """
        super().__init__(descriptor_file)

    @property
    def entry_service_file(self):
        """
        Provides the entry point service of the package.
        :return: service id
        """
        return self.content['entry_service_template'] if \
            'entry_service_template' in self.content else None

    @property
    def service_descriptors(self):
        """
        Provides a list of the service descriptor file names, referenced in
        the package.
        :return: list of service descriptor file names
        """
        service_list = []
        for item in self.content['package_content']:
            if item['content-type'] == \
                    'application/sonata.service_descriptor':
                service_list.append(item['name'])
        return service_list

    @property
    def function_descriptors(self):
        """
        Provides a list of the service descriptor file names, referenced in
        the package.
        :return: list of function descriptor file names
        """
        function_list = []
        for item in self.content['package_content']:
            if item['content-type'] == \
                    'application/sonata.function_descriptor':
                function_list.append(item['name'])
        return function_list

    @property
    def descriptors(self):
        """
        Provides a list of the descriptors, referenced in the package.
        :return: list of descriptor file names
        """
        return self.service_descriptors + self.function_descriptors

    def md5(self, descriptor_file):
        """
        Retrieves the MD5 hash defined in the package content of the specified
        descriptor
        :param descriptor_file: descriptor filename
        :return: md5 hash if descriptor found, None otherwise
        """
        descriptor_file = '/' + descriptor_file
        for item in self.content['package_content']:
            if item['name'] == descriptor_file:
                return item['md5']


class Service(Descriptor):

    def __init__(self, descriptor_file):
        """
        Initialize a service object. This inherits the descriptor object.
        :param descriptor_file: descriptor filename
        :param _functions:
        """
        super().__init__(descriptor_file)
        self._functions = {}
        self._vnf_id_map = {}
        self._fw_graphs = list()

    @property
    def functions(self):
        """
        Provides the functions specified in the service.
        :return: functions dict
        """
        return self._functions
    @property
    def fw_graphs(self):
        """
        Provides the forwarding paths specified in the service.
        :return: forwarding paths dict
        """
        return self._fw_graphs

    @property
    def all_function_connection_points(self):
        func_cps = []
        for fid, f in self.functions.items():
            func_cps += f.connection_points

        return func_cps
    @property
    def vnf_id_map(self):
        return self._vnf_id_map

    def mapped_function(self, vnf_id):
        """
        Provides the function associated with a 'vnf_id' defined in the
        service content.
        :param vnf_id: vnf id
        :return: function object
        """
        if vnf_id not in self._vnf_id_map or self._vnf_id_map[vnf_id] not in\
                self._functions:
            return
        return self._functions[self._vnf_id_map[vnf_id]]

    def detect_loops(self):
        loops = {}
        vnfs = self.vnf_id_map.keys()
        for vnf in vnfs:
            for vl_id, vl in self.vlinks.items():
                cp_aux = []
                cpr_u_splitted = vl.cpr_u.split(":")
                cpr_v_splitted = vl.cpr_v.split(":")
                if cpr_u_splitted[0]==cpr_v_splitted[0]:
                    loops[vl_id]= [vl.cpr_u, vl.cpr_v]
                    return loops

            for vb_id, vb in self.vbridges.items():
                cp_aux = []
                for cp in self.connection_points:
                    if vb.cp_refs.count(cp)>1:
                        loops[vb_id] = [cp,cp]
                        return loops
                for cp in vb.cp_refs:
                    cp_splitted = cp.split(":")
                    if len(cp_splitted) == 2 and cp_splitted[0]==cp_splitted[1]:
                        loops[vb_id] = [cp_splitted[0], cp_splitted[1]]
                        return loops
                    if vnf == cp_splitted[0]:
                        cp_aux.append(cp)
                if len(cp_aux) >= 2:
                    loops[vb_id] = cp_aux
        return loops
    def detect_isolated_vnfs(self):
        isolated_vnfs = []
        for function_name, function_id in self.vnf_id_map.items():
            vnfd_cps = self.functions[function_id].connection_points
            vnfd_is_isolated = True
            for cp in vnfd_cps:
                cp_extended = function_name +":"+cp
                for vl_id, vl in self.vlinks.items():
                    if cp_extended == vl.cpr_u or cp_extended == vl.cpr_v:
                            vnfd_is_isolated = False
                            break
                if vnfd_is_isolated:
                    for vb_id, vb in self.vbridges.items():
                        if cp_extended in vb.cp_refs:
                            vnfd_is_isolated = False
                            break
            if vnfd_is_isolated:
                isolated_vnfs.append(function_name)
        return isolated_vnfs

    def detect_unnused_cps(self):
        #986812400
        unnused_cps = []
        for function_name, function_id in self.vnf_id_map.items():
            for cp in self.functions[function_id].connection_points:
                cp_extended = function_name+":"+cp
                cp_is_used = False
                for vl_id, vl in self.vlinks.items():
                    if vl.cpr_u == cp_extended or vl.cpr_v == cp_extended:
                        cp_is_used = True
                        break
                if not cp_is_used:
                    for vb_id, vb in self._vbridges.items():
                        if not cp_is_used:
                            for cp in vb.cp_refs:
                                if cp == cp_extended:
                                    cp_is_used = True
                                    break
                if not cp_is_used:
                    unnused_cps.append(cp_extended)
        return unnused_cps
    def vnf_id(self, func):
        """
        Provides the vnf id associated with the provided function.
        :param func: function object
        :return: vnf id
        """
        for vnf_id, fid in self._vnf_id_map.items():
            if fid == func.id:
                return vnf_id
        return

    def associate_function(self, func, vnf_id):
        """
        Associate a function to the service.
        :param func: function object
        :param vnf_id: vnf id, defined in the service descriptor content
        """
        if type(func) is not Function:
            log.error("The function (VNF) id='{0}' has an invalid type"
                      .format(func.id))
            return

        if func.id in self.functions:
            log.error("The function (VNF) id='{0}' is already associated with "
                      "service id='{1}'".format(func.id, self.id))
            return

        log.debug("Service '{0}': associating function id='{1}' with vnf_id="
                  "'{2}'".format(self.id, func.id, vnf_id))

        self._functions[func.id] = func
        self._vnf_id_map[vnf_id] = func.id

    def build_topology_graph(self, level=1, bridges=False,
                             vdu_inner_connections=True):
        """
        Build the network topology graph of the service.
        :param level: indicates the granulariy of the graph
                    0: service level (does not show VNF interfaces)
                    1: service level (with VNF interfaces) - default
                    2: VNF level (showing VDUs but not VDU interfaces)
                    3: VDU level (with VDU interfaces)
        :param bridges: indicates whether bridges should be included in
                        the graph
        :param vdu_inner_connections: indicates whether VDU connection points
                                      should be internally connected
        """
        assert 0 <= level <= 3  # level must be 0, 1, 2, 3

        graph = nx.Graph()

        def_node_attrs = {'label': '',
                          'level': level,
                          'parent_id': self.id,
                          'type': ''  # 'iface' | 'br-iface' | 'bridge'
                          }

        def_link_attrs = {'label': '',
                          'level': '',
                          'type': ''  # 'iface' | 'br-iface' | 'vdu_in'
                          }

        # assign nodes from service connection points
        connection_point_refs = self.vlink_cp_refs
        if bridges:
            connection_point_refs += self.vbridge_cp_refs
        for cpr in connection_point_refs:
            node_attrs = def_node_attrs.copy()
            node_attrs['label'] = cpr
            s_cpr = cpr.split(':')
            func = self.mapped_function(s_cpr[0])
            if len(s_cpr) > 1 and func:

                node_attrs['parent_id'] = self.id
                node_attrs['level'] = 1
                node_attrs['node_id'] = func.id
                node_attrs['node_label'] = func.content['name']

            else:
                node_attrs['parent_id'] = ""
                node_attrs['level'] = 0
                node_attrs['node_id'] = self.id
                node_attrs['node_label'] = self.content['name']

            node_attrs['label'] = s_cpr[1] if len(s_cpr) > 1 else cpr

            if cpr in self.vlink_cp_refs:
                node_attrs['type'] = 'iface'
            elif cpr in self.vbridge_cp_refs:
                node_attrs['type'] = 'br-iface'

            graph.add_node(cpr, attr_dict=node_attrs)

        prefixes = []
        # assign sub-graphs of functions
        for fid, func in self.functions.items():
            # done to work with current descriptors of sonata demo
            prefix_map = {}
            prefix = self.vnf_id(func)

            if level <= 2:
                func.graph = func.build_topology_graph(
                    parent_id=self.id,
                    bridges=bridges,
                    level=0,
                    vdu_inner_connections=vdu_inner_connections)
            else:
                func.graph = func.build_topology_graph(
                    parent_id=self.id,
                    bridges=bridges,
                    level=1,
                    vdu_inner_connections=vdu_inner_connections)

            if level == 0:
                for node in func.graph.nodes():
                    node_tokens = node.split(':')
                    if len(node_tokens) > 1 and node in graph.nodes():
                        graph.remove_node(node)
                    else:
                        pn = prefix + ':' + node
                        if graph.has_node(pn):
                            graph.remove_node(pn)
                prefixes.append(prefix)

            elif level == 1:
                prefixes.append(prefix)

            elif level == 2:
                for node in func.graph.nodes():
                    s_node = node.split(':')
                    if len(s_node) > 1:
                        prefix_map[node] = prefix + ':' + s_node[0]
                    else:
                        prefix_map[node] = prefix + ':' + node

                re_f_graph = nx.relabel_nodes(func.graph, prefix_map,
                                              copy=True)
                graph.add_nodes_from(re_f_graph.nodes(data=True))
                graph.add_edges_from(re_f_graph.edges(data=True))

            elif level == 3:
                for node in func.graph.nodes():
                    s_node = node.split(':')
                    if node in func.connection_points and len(s_node) > 1:
                        prefix_map[node] = node
                    else:
                        prefix_map[node] = prefix + ':' + node

                re_f_graph = nx.relabel_nodes(func.graph, prefix_map,
                                              copy=True)
                graph.add_nodes_from(re_f_graph.nodes(data=True))
                graph.add_edges_from(re_f_graph.edges(data=True))

        # build vlinks topology graph
        if not self.vlinks and not self.vbridges:
            log.warning("No links were found")
        for vl_id, vl in self.vlinks.items():

            if level >= 1:
                cpr_u = vl.cpr_u
                cpr_v = vl.cpr_v

            elif level == 0:
                cpr_u = vl.cpr_u.split(':')
                cpr_v = vl.cpr_v.split(':')

                if len(cpr_u) > 1 and cpr_u[0] in prefixes:
                    cpr_u = cpr_u[0]
                else:
                    cpr_u = vl.cpr_u

                if len(cpr_v) > 1 and cpr_v[0] in prefixes:
                    cpr_v = cpr_v[0]
                else:
                    cpr_v = vl.cpr_v
            else:
                return

            link_attrs = def_link_attrs.copy()
            link_attrs['label'] = vl.id
            link_attrs['level'] = 0 if level == 0 else 1
            link_attrs['type'] = 'iface'
            graph.add_edge(cpr_u, cpr_v, attr_dict=link_attrs)

        # build vbridges topology graph
        if bridges:
            for vb_id, vb in self.vbridges.items():
                brnode = 'br-' + vb_id
                node_attrs = def_node_attrs.copy()
                node_attrs['label'] = brnode
                node_attrs['level'] = 1
                node_attrs['type'] = 'bridge'

                # add 'router' node for this bridge
                graph.add_node(brnode, attr_dict=node_attrs)
                for cp in vb.connection_point_refs:
                    if level >= 1:
                        s_cp = cp
                    elif level == 0:
                        s_cp = cp.split(':')
                        if len(s_cp) > 1 and s_cp[0] in prefixes:
                            s_cp = s_cp[0]
                        else:
                            s_cp = cp
                    else:
                        return

                    link_attrs = def_link_attrs
                    link_attrs['label'] = vb_id
                    link_attrs['level'] = 0 if level == 0 else 1
                    link_attrs['type'] = 'br-iface'
                    graph.add_edge(brnode, s_cp, attr_dict=link_attrs)

        # inter-connect VNF interfaces
        if level == 1:
            for node_u in graph.nodes():
                node_u_tokens = node_u.split(':')

                if len(node_u_tokens) > 1 and node_u_tokens[0] in prefixes:

                    for node_v in graph.nodes():
                        if node_u == node_v:
                            continue
                        node_v_tokens = node_v.split(':')
                        if len(node_v_tokens) > 1 and \
                                node_v_tokens[0] == node_u_tokens[0]:

                            # verify if these interfaces are connected
                            func = self.mapped_function(node_v_tokens[0])

                            if func.graph.has_node(node_u_tokens[1]):
                                node_u_c = node_u_tokens[1]
                            elif func.graph.has_node(node_u):
                                node_u_c = node_u
                            else:
                                continue

                            if func.graph.has_node(node_v_tokens[1]):
                                node_v_c = node_v_tokens[1]
                            elif func.graph.has_node(node_v):
                                node_v_c = node_v
                            else:
                                continue

                            if nx.has_path(func.graph, node_u_c, node_v_c):
                                link_attrs = def_link_attrs
                                link_attrs['label'] = node_u + '-' + node_v
                                link_attrs['level'] = 1
                                link_attrs['type'] = 'iface'
                                graph.add_edge(node_u, node_v,
                                               attr_dict=link_attrs)
        return graph

    def load_forwarding_graphs(self):
        """
        Load all forwarding paths of all forwarding graphs, defined in the
        service content.
        """
        for fgraph in self.content['forwarding_graphs']:
            s_fwgraph = dict()
            s_fwgraph['fg_id'] = fgraph['fg_id']
            s_fwgraph['fw_paths'] = list()

            for fpath in fgraph['network_forwarding_paths']:
                s_fwpath = dict()
                s_fwpath['fp_id'] = fpath['fp_id']

                path_dict = {}
                for cp in fpath['connection_points']:
                    cpr = cp['connection_point_ref']
                    s_cpr = cpr.split(':')
                    pos = cp['position']

                    if len(s_cpr) == 1 and cpr not in self.connection_points:
                        evtlog.log("Undefined connection point",
                                   "Connection point '{0}' of forwarding path "
                                   "'{1}' is not defined"
                                   .format(cpr, fpath['fp_id']),
                                   self.id,
                                   'evt_nsd_top_fwgraph_cpoint_undefined')
                        return
                    elif len(s_cpr) == 2:
                        # get corresponding function
                        func = self.mapped_function(s_cpr[0])
                        if not func or (func and s_cpr[1]
                                        not in func.connection_points):
                            evtlog.log("Undefined connection point",
                                       "Connection point '{0}' of forwarding "
                                       "path '{1}' is not defined"
                                       .format(cpr, fpath['fp_id']),
                                       self.id,
                                       'evt_nsd_top_fwgraph_cpoint_undefined')
                            return

                    if pos in path_dict:
                        evtlog.log("Duplicate reference in FG",
                                   "Duplicate referenced position '{0}' "
                                   "in forwarding path id='{1}'. Ignoring "
                                   "connection point: '{2}'"
                                   .format(pos, fpath['fp_id'],
                                           path_dict[pos]),
                                   self.id,
                                   'evt_nsd_top_fwgraph_position_duplicate')
                    path_dict[pos] = cpr
                d = OrderedDict(sorted(path_dict.items(),
                                       key=lambda t: t[0]))

                s_fwpath['path'] = list(d.values())
                s_fwgraph['fw_paths'].append(s_fwpath)

            self._fw_graphs.append(s_fwgraph)

        return True

    def _cp_in_functions(self, iface):
        """
        Indicates whether the provided connection point is defined in the
        functions of the service.
        :param iface: interface
        :return: True, if a functions contains the interface
                 False, otherwise.
        """
        iface_tokens = iface.split(':')
        if len(iface_tokens) != 2:
            return False
        func = self.mapped_function(iface_tokens[0])
        if not func:
            return False
        if (iface_tokens[1] not in func.interfaces and
                iface not in func.interfaces):
            return False

        return True

    def trace_path(self, path):
        """
        Trace a forwarding path along the service topology.
        This function returns a list with the visited interfaces. In cases
        where the path contains 'impossible' links it will add the 'BREAK'
        keyword in the according position of the trace list.
        :param path: forwarding path ordered interface list
        :return: trace list
        """
        trace = []
        for x in range(len(path)-1):
            trace.append(path[x])
            if not self._graph.has_node(path[x]):
                trace.append("BREAK")
                continue
            neighbours = self._graph.neighbors(path[x])
            if path[x+1] not in neighbours:
                trace.append("BREAK")
        trace.append(path[-1])
        return trace

    def trace_path_pairs(self, path):
        trace = []
        for x in range(0, len(path), 2):
            if x+1 >= len(path):
                node_pair = {'break': False, 'from': path[x], 'to': None}
            else:
                node_pair = {'break': False, 'from': path[x], 'to': path[x+1]}
                neighbors = self._graph.neighbors(path[x])
                if path[x] not in self.graph.nodes():
                    node_pair['break'] = True
                elif path[x+1] not in self._graph.neighbors(path[x]) and self._graph.neighbors(path[x]):
                    for neighbor in neighbors:
                        if neighbor[0:1]=="br":
                            if path[x+1] in self.graph.neighbors(neighbor):
                                break
                    node_pair['break'] = False
            trace.append(node_pair)
        return trace

    def undeclared_connection_points(self):
        """
        Provides a list of connection points that are referenced in
        'virtual_links' section but not declared in 'connection_points'
        of the Service or its Functions.
        """
        target_cp_refs = self.vlink_cp_refs + self.vbridge_cp_refs
        undeclared_cps = []
        for cpr in target_cp_refs:
            cpr_split = cpr.split(':')
            if len(cpr_split) == 1 and cpr not in self.connection_points:
                undeclared_cps.append(cpr)
            else:
                f = self.mapped_function(cpr_split[0])
                if f and cpr_split[1] not in f.connection_points:
                    undeclared_cps.append(cpr)

        return undeclared_cps


class Function(Descriptor):

    def __init__(self, descriptor_file):
        """
        Initialize a function object. This inherits the descriptor object.
        :param descriptor_file: descriptor filename
        """
        super().__init__(descriptor_file)
        self._units = {}

    @property
    def units(self):
        """
        Provides the unit objects associated with the function.
        :return: units dict
        """
        return self._units

    def associate_unit(self, unit):
        """
        Associate a unit to the function.
        :param unit: unit object
        """
        if not isinstance(unit,Unit):
            return

        if unit.id in self.units:
            if isinstance(unit,VDU_unit):
                log.error("The unit (VDU) id='{0}' is already associated with "
                          "function (VNF) id='{1}'".format(unit.id, self.id))
            else:
                log.error("The unit (CDU) id='{0}' is already associated with "
                          "function (VNF) id='{1}'".format(unit.id, self.id))
            return

        self._units[unit.id] = unit
        return True

    def load_units(self):
        """
        Load units of the function descriptor content, section
        'virtual_deployment_units or cloudnative_deployment_units'
        """
        vduExist = 'virtual_deployment_units' in self.content
        cduExist = 'cloudnative_deployment_units' in self.content

        if vduExist:
            for vdu in self.content['virtual_deployment_units']:
                unit = VDU_Unit(vdu['id'])
                self.associate_unit(unit)

                # Check vm image URLs
                # only perform a check if vm_image is a URL
                vdu_image_path = vdu['vm_image']
                if validators.url(vdu_image_path):  # Check if is URL/URI.
                    try:
                        # Check if the image URL is accessible
                        # within a short time interval
                        requests.head(vdu_image_path, timeout=1)

                    except (requests.Timeout, requests.ConnectionError):

                        evtlog.log("VDU image not found",
                                   "Failed to verify the existence of VDU image at"
                                   " the address '{0}'. VDU id='{1}'"
                                   .format(vdu_image_path, vdu['id']),
                                   self.id,
                                   'evt_vnfd_itg_vdu_image_not_found')
            return True

        elif cduExist:
            for cdu in self.content['cloudnative_deployment_units']:
                unit = CDU_Unit(cdu['id'])
                if self.associate_unit(unit):
                    if 'parameters' in cdu :
                        if cdu['parameters'].get('env'):
                            unit.set_env(cdu['parameters'].get('env'))
                        if cdu['parameters'].get('k8s_deployment'):
                            unit.set_k8s_deployment(cdu['parameters'].get('k8s_deployment'))
                        if cdu['parameters'].get('k8s_service'):
                            unit.set_k8s_service(cdu['parameters'].get('k8s_service'))
            return True

        else:
            log.error("Function id={0} is missing the "
                      "'virtual_deployment_units or cloudnative_deployment_units' section"
                      .format(self.id))
            return
    def get_units_by_ports(self, port_to_find):
        """
        Return a dictionary with all the CDUs which use a particular port.
        :return: dictionary: key = port, value = [cdu01, cdu02...]
        """
        dic_port_unit = {}

        for unit_id, unit in self.units.items():
            if isinstance(unit, CDU_Unit):
                for cp_id, port in unit.ports.items():
                    if port in port_to_find:
                        if port not in dic_port_unit.keys():
                            dic_port_unit[port] = [unit_id]
                        else:
                            dic_port_unit[port].append(unit_id)
        return dic_port_unit
    def load_unit_connection_points(self):
            """
            Load connection points of the units of the function.
            """
            vduExist = 'virtual_deployment_units' in self.content
            cduExist = 'cloudnative_deployment_units' in self.content
            if vduExist:
                for vdu in self.content['virtual_deployment_units']:
                    if vdu['id'] not in self.units.keys():
                        log.error("Unit id='{0}' is not associated with function "
                                  "id='{1}".format(vdu['id'], self.id))
                        return

                    unit = self.units[vdu['id']]
                    if 'connection_points' not in vdu:
                        return
                    for cp in vdu['connection_points']:
                        unit.add_connection_point(cp['id'])
                return True
            elif cduExist:
                for cdu in self.content['cloudnative_deployment_units']:
                    if cdu['id'] not in self.units.keys():
                        log.error("Unit id='{0}' is not associated with function "
                                  "id='{1}".format(cdu['id'], self.id))
                        return

                    unit = self.units[cdu['id']]
                    if cdu.get('connection_points'):
                        for cp in cdu['connection_points']:
                            unit.add_connection_point(cp['id'])
                            if 'port' in cp:
                                unit.add_port(cp['id'],cp['port'])
                    else:
                        return
                return True
            else:
                return
    def detect_loops(self):
        """
        detect wheter some vlink or vbridge are forming a loop
        :return: the id of the vlink/vtree which makes the loop and the points of the vdu
        """
        selfloops = {}
        for vl_id, vl in self.vlinks.items():
            cpr_u = vl.cpr_u.split(":")
            cpr_v = vl.cpr_v.split(":")
            if cpr_u[0]==cpr_v[0]:
                if vl_id not in selfloops.keys():
                    selfloops[vl_id]=[vl.cpr_u,vl.cpr_v]
                else:
                    selfloops[vl_id].append([vl.cpr_u,vl.cpr_v])
        for vb_id, vb in self.vbridges.items():
            for i in range(0,len(vb.connection_point_refs)):
                if vb_id in selfloops.keys():
                    continue
                cp = vb.connection_point_refs[i].split(":")
                id = cp[0]
                for j in range(0,len(vb.connection_point_refs)):
                    if i==j:
                        continue
                    cp_aux = vb.connection_point_refs[j].split(":")
                    id_aux = cp_aux[0]
                    if id==id_aux:
                        if vb_id not in selfloops.keys():
                            selfloops[vb_id]=[vb.connection_point_refs[i],vb.connection_point_refs[j]]
                        else:
                            selfloops[vb_id].append(vb.connection_point_refs[j])
        return selfloops

    def detect_disconnected_units(self):
        """
        detect wheter some unit is disconnected (all cp are unused)
        :return: id of the units which are disconnected
        """
        unused_units = []
        for unit_id, unit in self.units.items():
            cp_used_unit = []
            cp_used_unit = []
            for cp in unit.connection_points:
                cp_extended = unit_id+":"+cp
                unit_is_isolated = True
                for vl_id, vl in self.vlinks.items():
                    if cp_extended in vl.connection_point_refs and cp not in cp_used_unit:
                        cp_used_unit.append(cp)
                        break
                for vb_id, vb in self.vbridges.items():
                    if cp_extended in vb.connection_point_refs and cp not in cp_used_unit:
                        cp_used_unit.append(cp)
                        break
            if len(cp_used_unit)==0:

                unused_units.append(unit_id)
        return unused_units

    def search_duplicate_ports(self):
        """
        Check wheter two (or more) CDUs have replicate ports i.e. cdu:01 -> 5000 and cdu:02 -> 5000
        :return: Dic with key = cdu_id, value = replicate_port
        """
        checked_ports = []
        duplicate_ports = []
        for unit_id, unit in self.units.items():
            if isinstance(unit,CDU_Unit):
                for cp_id, port in unit.ports.items():
                    if port in checked_ports and not (port in duplicate_ports):
                        duplicate_ports.append(port)

                    else:
                        checked_ports.append(port)

        return duplicate_ports

    def detect_unnused_cps_units(self):
        """
        detect wheter some cp in some unit is disconnected:
        :return:
        """
        unnused_cps = []
        for unit_id, unit in self.units.items():
            for cp in unit.connection_points:
                cp_is_used = False
                cp_extended = unit_id+":"+cp
                for vl_id, vl in self.vlinks.items():
                    if cp_extended in vl.connection_point_refs:
                        cp_is_used = True
                        break
                if not cp_is_used:
                    for vb_id, vb in self.vbridges.items():
                        if cp_extended in vb.cp_refs:
                            cp_is_used = True
                            break
                if not cp_is_used:
                    unnused_cps.append(cp_extended)
        return unnused_cps

    def build_topology_graph(self, bridges=False, parent_id='', level=0,
                             vdu_inner_connections=True):
        """
        Build the network topology graph of the function.
        :param bridges: indicates if bridges should be included in the graph
        :param parent_id: identify the parent service of this function
        :param level: indicates the granularity of the graph
                    0: VNF level (showing VDUs but not VDU connection points)
                    1: VDU level (with VDU connection points)
        :param vdu_inner_connections: indicates whether VDU connection points
                                      should be internally connected
        """
        graph = nx.Graph()
        def_node_attrs = {'label': '',
                          'level': level,
                          'parent_id': self.id,
                          'type': ''  # 'iface' | 'br-iface' | 'bridge'
                          }
        def_edge_attrs = {'label': '',
                          'level': '',
                          'type': ''}
        # assign nodes from function

        cp_refs = self.vlink_cp_refs
        if bridges:
            cp_refs += self.vbridge_cp_refs
        for cpr in cp_refs:
            node_attrs = def_node_attrs.copy()
            s_cpr = cpr.split(':')
            unit = self.units[s_cpr[0]] if s_cpr[0] in self.units else None
            if len(s_cpr) > 1 and unit:
                if level == 0:
                    iface = s_cpr[0]
                node_attrs['parent_id'] = self.id
                node_attrs['level'] = 2
                node_attrs['node_id'] = unit.id
                node_attrs['node_label'] = unit.id
            else:
                node_attrs['parent_id'] = parent_id
                node_attrs['level'] = 1
                node_attrs['node_id'] = self.id
                node_attrs['node_label'] = self.content['name']
            node_attrs['label'] = s_cpr[1] if len(s_cpr) > 1 else cpr

            if cpr in self.vlink_cp_refs:
                node_attrs['type'] = 'iface'
            elif cpr in self.vbridge_cp_refs:
                node_attrs['type'] = 'br-iface'
            graph.add_node(cpr, attr_dict=node_attrs)
        for vl_id, vl in self.vlinks.items():
            edge_attrs = def_edge_attrs.copy()

            cpr_u = vl.cpr_u.split(':')
            cpr_v = vl.cpr_v.split(':')

            if level == 0:
                if vl.cpr_u not in self.connection_points and len(cpr_u) > 1:
                    cpr_u = cpr_u[0]
                else:
                    cpr_u = vl.cpr_u

                if vl.cpr_v not in self.connection_points and len(cpr_v) > 1:
                    cpr_v = cpr_v[0]
                else:
                    cpr_v = vl.cpr_v
                edge_attrs['level'] = 1

            elif level == 1:
                # unit interfaces are nodes
                cpr_u = vl.cpr_u
                cpr_v = vl.cpr_v
                edge_attrs['level'] = 2

            edge_attrs['type'] = 'iface'
            edge_attrs['label'] = vl.id
            graph.add_edge(cpr_u, cpr_v, attr_dict=edge_attrs)
        if vdu_inner_connections:
            # link vdu interfaces if level 1
            if level == 1:
                for uid, unit in self.units.items():
                    edge_attrs = def_edge_attrs.copy()
                    join_cps = []
                    for cp in unit.connection_points:
                        # patch for faulty descriptors regarding sep ':'
                        s_cp = cp.split(':')
                        if len(s_cp) > 1:
                            join_cps.append(cp)
                        else:
                            join_cps.append(uid + ':' + cp)

                    for u_cp in join_cps:
                        for v_cp in join_cps:
                            if u_cp == v_cp:
                                continue
                            if graph.has_edge(u_cp, v_cp):
                                continue
                            if not bridges and (
                                    u_cp in self.vbridge_cp_refs or
                                    v_cp in self.vbridge_cp_refs):
                                continue
                            edge_attrs['level'] = 2
                            edge_attrs['label'] = 'VDU_IN'
                            edge_attrs['type'] = 'vdu_in'
                            graph.add_edge(u_cp, v_cp)

        # build bridge topology graph
        if bridges:
            for vb_id, vb in self.vbridges.items():
                # add bridge router
                brnode = "br-" + vb_id
                node_attrs = def_node_attrs.copy()
                node_attrs['label'] = brnode
                node_attrs['level'] = 2
                node_attrs['type'] = 'bridge'
                graph.add_node(brnode, attr_dict=node_attrs)

                for cpr in vb.connection_point_refs:
                    s_cpr = cpr.split(':')
                    if level == 0 and len(s_cpr) > 1:
                        s_cpr = s_cpr[0]
                    else:
                        s_cpr = cpr

                    graph.add_edge(brnode, s_cpr, attr_dict={'label': vb_id})
        return graph

    def undeclared_connection_points(self):
        """
        Provides a list of interfaces that are referenced in 'gitvirtual_links'
        section but not declared in 'connection_points' of the Function and its
        Units.
        """
        target_cp_refs = self.vlink_cp_refs + self.vbridge_cp_refs
        undeclared_cps = []
        for cpr in target_cp_refs:
            cpr_split = cpr.split(':')
            if len(cpr_split) == 1 and cpr not in self.connection_points:
                undeclared_cps.append(cpr)
            elif len(cpr_split) == 2:
                if not cpr_split[0] in self.units:
                    undeclared_cps.append(cpr)
                else:
                    vdu = self.units[cpr_split[0]]
                    if cpr_split[1] not in vdu.connection_points:
                        undeclared_cps.append(cpr)
        return undeclared_cps

class Unit(Node):
    def __init__(self, uid):
        """
        Initialize a unit object. This inherits the node object.
        :param uid: unit id
        """
        super().__init__(uid)

class VDU_Unit(Unit):
    def __init__(self, uid):
        """
        Initialize an vdu_unit object.
        :param uid: unit id
        """
        super().__init__(uid)

class CDU_Unit(Unit):
    def __init__(self, uid):
        """
        Initialize an cdu_unit object.
        :param uid: unit id
        """
        super().__init__(uid)
        self._ports = {}
        self._k8s_deployment = {}
        self._k8s_service = {}
        self._env = {}
    @property
    def ports(self):
        """
        Ports of the connection points
        """
        return self._ports
    @property
    def env(self):
        """
        :return: env
        """
        return self._env

    def set_env(self,env):
        """
        Set env
        """
        for env_id, env in env.items():
            self._env[env_id]=env
    @property
    def k8s_deployment(self):
        """
        :return: k8s_deployment
        """
        return self._k8s_deployment

    def set_k8s_deployment(self, k8s_deployment):
        """
        Set k8s_deployment
        """
        for k8s_deployment_id, k8s_deployment in k8s_deployment.items():
            self._k8s_deployment[k8s_deployment_id] = k8s_deployment
    @property
    def k8s_service(self):
        """
        :return: k8s_service
        """
        return self._k8s_service

    def set_k8s_service(self, k8s_service):
        """
        Set the value of the k8s_service
        """
        for k8s_service_id, k8s_service in k8s_service.items():
            self._k8s_service[k8s_service_id] = k8s_service

    def add_port(self, id, port):
        self._ports[id] = port

class Probe:
    def __init__(self):
        self._id = ""
        self._name = ""
        self._image = ""
        self._description = ""
        self._parameters = {}

    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @property
    def image(self):
        return self._image
    @property
    def description(self):
        return self._description
class Step:
    def __init__(self):
        self._name = ""
        self._description = ""
        self._action = ""
        self._probes = []
        self._step = ""
        self._action = ""
        self._instantation_parameters = []
        self._run = ""
        self._index = {}
        self._start__delay = {}
        self._dependencies = {}
        self._output = ""

        @property
        def id(self):
            return self._id
        @property
        def name(self):
            return self._name
        @property
        def image(self):
            return self._image
        @property
        def description(self):
            return self._description
        @property
        def step(self):
            return self._step
        @property
        def action(self):
            return self._action
        @property
        def run(self):
            return self._run
class Phase:
    def __init__(self, phase):
        self._id = phase["id"]
        self._steps = []
    @property
    def id(self):
        return self._id

    def add_step(self,step):
        self._steps.append(step)

    def load_steps(self, steps):
        for step in steps:
            new_step = Step()
            if "action" in step.keys():
                new_step.action = step["action"]
            if "description" in step.keys():
                new_step.description = step["description"]
            if "name" in step.keys():
                new_step.name = step["name"]
            if "probes" in step.keys():
                for probe in step["probes"]:
                    new_probe = Probe()
class Test:
    def __init__(self, descriptor_file):
        self._id = None
        self._test_category = None
        self._content = None
        self.filename = descriptor_file
        self._phases = []
        self._service_platforms = []
        self._test_tags = {}
        self._test_category = {}
        self._name = None

    def add_test_tag(self, type, description):
        self._test_tags[type] = description
    def add_service_platform(self, service_platform):
        self._service_platforms.append(service_platform)
    def add_test_category(self, test_category):
        self._test_category.append(test_category)
    @property
    def id(self):
        return self._id

    @property
    def test_type(self):
        return self._test_type

    @property
    def test_category(self):
        return self._test_category

    @property
    def name(self):
        return self._name
    @property
    def content(self):
        """
        Descriptor dictionary.
        :return: descriptor dict
        """
        return self._content

    @property
    def filename(self):
        """
        Filename of the descriptor
        :return: descriptor filename
        """
        return self._filename
    @property
    def phases(self):
        return self._phases
    @content.setter
    def content(self, content):
        """
        Sets the descriptor dictionary.
        This modification will impact the id of the descriptor.
        :param value: content, an OrderedDict
        """
        self._content = content
        self._id = descriptor_id(self._content)


    @filename.setter
    def filename(self, value):
        """
        Sets the descriptor filename.
        This modification will impact the content and id of the descriptor.
        :param value: descriptor filename
        """
        self._filename = value
        content = read_descriptor_file(self._filename)
        if content:
            self.content = content

    @name.setter
    def name(self, value):
        self._name = value
    def get_phase_by_id(self, id):
        for phase in self.phases:
            if phase.id == id:
                return phase
        return
    def load_phases(self):
        """
        Load the phases of the descriptor
        """
        if not self.content["phases"]:
            return False
        for phase in self.content["phases"]:
            if self.get_phase_by_id(phase["id"]):
                evtlog.log("Replicate 'phase id'",
                           "Couldn't load the phases of "
                           "test descriptor id='{0}'"
                           .format(self.id),
                           self.id,
                           'evt_tstd_itg_badsection_phases_replicate_id')
                return
            else:
                new_phase = Phase(phase)
                if "steps" not in phase.keys():
                    evtlog.log("Missing 'steps'",
                               "Couldn't load the steps of "
                               "test descriptor id='{0}'"
                               .format(self.id),
                               self.id,
                               'evt_tstd_itg_badsection_steps_missing')
                    return
                new_phase.load_steps(phase["steps"])
                self.phases.append(Phase(phase))
        return True
class Slice_vld:
    def __init__(self):
        self._id = None
        self._name = None
        self._mgt_network = None
        self._type = None
        self._root_bandwidth = None
        self._root_bandwidth_unit = None
        self._leaf_bandwidth = None
        self._leaf_bandwidth_unit = None
        self._physical_network = None
        self._segmentation_id = None
        self._nsd_connection_point_ref = None

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def mgt_network(self):
        return self._mgt_network
    @mgt_network.setter
    def mgt_network(self, value):
        self._mgt_network = value

    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, value):
        self._type = value

    @property
    def root_bandwidth(self):
        return self._root_bandwidth
    @root_bandwidth.setter
    def root_bandwidth(self, value):
        self._root_bandwidth = value

    @property
    def root_bandwidth_unit(self):
        return self._root_bandwidth_unit
    @root_bandwidth_unit.setter
    def root_bandwidth_unit(self, value):
        self._root_bandwidth_unit = value

    @property
    def leaf_bandwidth(self):
        return self._leaf_bandwidth
    @leaf_bandwidth.setter
    def leaf_bandwidth(self, value):
        self._leaf_bandwidth = value

    @property
    def leaf_bandwidth_unit(self):
        return self._leaf_bandwidth_unit
    @leaf_bandwidth_unit.setter
    def leaf_bandwidth_unit(self, value):
        self._leaf_bandwidth_unit = value

    @property
    def phisical_network(self):
        return self._phisical_network
    @phisical_network.setter
    def phisical_network(self, value):
        self._phisical_network = value

    @property
    def segmentation_id(self):
        return self._segmentation_id
    @segmentation_id.setter
    def segmentation_id(self, value):
        self._segmentation_id = value

    @property
    def phisical_network(self):
        return self._phisical_network
    @phisical_network.setter
    def phisical_network(self, value):
        self._phisical_network = value

class Ns_subnet:
    def __init__(self):
        self._id = None
        self._nsd_ref = None
        self._nsd_name = None
        self._nsd_version = None
        self._nsd_vendor = None
        self._sla_name = None
        self._sla_ref = None
        self._is_shared = None

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def nsd_ref(self):
        return self._nsd_ref
    @nsd_ref.setter
    def nsd_ref(self, value):
        self._nsd_ref = value

    @property
    def nsd_name(self):
        return self._nsd_name
    @nsd_name.setter
    def nsd_name(self, value):
        self._nsd_name = value

    @property
    def nsd_version(self):
        return self._nsd_version
    @nsd_version.setter
    def nsd_version(self, value):
        self._nsd_version = value

    @property
    def nsd_vendor(self):
        return self._nsd_version
    @nsd_vendor.setter
    def nsd_vendor(self, value):
        self._nsd_vendor = value

    @property
    def sla_name(self):
        return self._sla_name
    @sla_name.setter
    def sla_name(self, value):
        self._sla_name = value

    @property
    def sla_ref(self):
        return self._sla_ref
    @sla_ref.setter
    def sla_ref(self, value):
        self._sla_ref = value

    @property
    def is_shared(self):
        return self._sla_ref
    @is_shared.setter
    def is_shared(self, value):
        self._is_shared = value


class Slice:
    def __init__(self, descriptor_file):
        self._id = None
        self._content = None
        self._filename = None
        self.filename = descriptor_file
        self._SNSSAI_identifier = {}
        self._onboardingState = None
        self._operationalState = None
        self._usageState = None
        self._5qi_value = None
        self._slice_ns_subnets = []
        self._slice_vld = []


    @property
    def SNSSAI_identifier(self):
        return self._id
    @SNSSAI_identifier.setter
    def SNSSAI_identifier(self, value):
        self._SNSSAI_identifier = value
    @property
    def id(self):
        return self._id
    @property
    def filename(self):
        """
        Filename of the descriptor
        :return: descriptor filename
        """
        return self._filename

    @property
    def content(self):
        """
        Content of the descriptor
        :return: descriptor content
        """
        return self._content

    @property
    def onboardingState(self):
        return self._onboardingState
    @onboardingState.setter
    def onboardingState(self, value):
        self._onboardingState = value

    @property
    def operationalState(self):
        return self._operationalState
    @operationalState.setter
    def operationalState(self, value):
        self._operationalState = value

    @property
    def usageState(self):
        return self._usageState
    @usageState.setter
    def usageState(self, value):
        self._usageState = value

    @property
    def _5qui_value(self):
        return self._5qui_value
    @_5qui_value.setter
    def _5qui_value(self, value):
        self._5qui_value = value


    @content.setter
    def content(self, content):
        """
        Sets the descriptor dictionary.
        This modification will impact the id of the descriptor.
        :param value: content, an OrderedDictsubnet
        """
        self._content = content
        self._id = descriptor_id(self._content)

    @filename.setter
    def filename(self, value):
        """
        Sets the descriptor filename.
        This modification will impact the content and id of the descriptor.
        :param value: descriptor filename
        """
        self._filename = value
        content = read_descriptor_file(self._filename)
        if content:
            self.content = content

    def check_subnet_id(self, id):
        """
        :id: id of the subnet
        :return: True if the id exists, False otherwise
        """

        for subnet in self._slice_ns_subnets:
            if id == subnet.id:
                return True
        return False

    def check_vld_id(self, id):
        """
        :id: id of the vld
        :return: True if the id exists, False otherwise
        """

        for vld in self._slice_vld:
            if id == vld.id:
                return True
        return False
    def load_config_values(self):
        SNSSAI_identifier = self.content.get("SNSSAI_identifier")
        if SNSSAI_identifier:
            self.SNSSAI_identifier = SNSSAI_identifier
        onboardingState = self.content.get("onboardingState")
        if onboardingState:
            self.onboardingState = onboardingState
        operationalState = self.content.get("operationalState")
        if operationalState:
            self.operationalState = operationalState
        usageState = self.content.get("usageState")
        if usageState:
            self.usageState = usageState
        _5qui_value = self.content.get("5qui_value")
        if _5qui_value:
            self._5qui_value = _5qui_value
    def load_ns_subnet(self, subnet):
        #It is not necessary check if the parameter exist because they are required in the schema.
        new_subnet = Ns_subnet()
        new_subnet.id = subnet.get("id")
        new_subnet.nsd_ref = subnet.get("nsd-ref")
        new_subnet.nsd_name = subnet.get("nsd-name")
        new_subnet.nsd_version = subnet.get("nsd-version")
        new_subnet.nsd_vendor = subnet.get("nsd-vendor")
        new_subnet.sla_name = subnet.get("sla-name")
        new_subnet.sla_ref = subnet.get("sla-ref")
        new_subnet.is_shared = subnet.get("is-shared")
        self._slice_ns_subnets.append(new_subnet)
        return True

    def load_vld(self, slice_vld):
        new_vld = Slice_vld()
        new_vld.id = slice_vld.get("id")
        new_vld.name = slice_vld.get("name")
        new_vld.type = slice_vld.get("type")
        new_vld._nsd_connection_point_ref = slice_vld.get("_nsd_connection_point_ref")
        self._slice_vld.append(new_vld)


class SLA:
    def __init__(self, descriptor_file):
        self._id = None
        self._content = None
        self._filename = None
        self.filename = descriptor_file
        self._offer_date = None
        self._expiration_date = None
        self._template_name = None
        self._provider_name = None
        self._template_initiator = None
        self._service = {}
        self._guaranteeTerms = []
        self._license = {}
    @property
    def id(self):
        return self._id
    @property
    def filename(self):
        """
        Filename of the descriptor
        :return: descriptor filename
        """
        return self._filename

    @property
    def content(self):
        """
        Content of the descriptor
        :return: descriptor content
        """
        return self._content

    @property
    def offer_date(self):
        return serf._offer_date
    @offer_date.setter
    def offer_date(self, value):
        self._offer_date = value

    @property
    def expiration_date(self):
        return self._expiration_date
    @expiration_date.setter
    def expiration_date(self, value):
        self._expiration_date = value

    @property
    def template_name(self):
        return self._template_name
    @template_name.setter
    def template_name(self, value):
        self._template_name = value
    @property
    def provider_name(self):
        return self._provider_name
    @property
    def template_initiator(self):
        return self._template_initiator
    @property
    def service(self):
        return self._service
    @property
    def license(self):
        return self._license



    @content.setter
    def content(self, content):
        """
        Sets the descriptor dictionary.
        This modification will impact the id of the descriptor.
        :param value: content, an OrderedDict
        """
        self._content = content
        self._id = descriptor_id(self._content)

    @filename.setter
    def filename(self, value):
        """
        Sets the descriptor filename.
        This modification will impact the content and id of the descriptor.
        :param value: descriptor filename
        """
        self._filename = value
        content = read_descriptor_file(self._filename)
        if content:
            self.content = content

    def load_config_values(self):
        offer_date = self.content.get("sla_template").get("offer_date")
        expiration_date = self.content.get("sla_template").get("expiration_date")
        template_name = self.content.get("sla_template").get("template_name")
        provider_name = self.content.get("sla_template").get("provider_name")
        template_initiator = self.content.get("sla_template").get("template_initiator")

        if offer_date:
            self._offer_date = offer_date
        if expiration_date:
            self._expiration_date = expiration_date
        if template_name:
            self._template_name = template_name
        if provider_name:
            self._provider_name = provider_name
        if template_initiator:
            self._template_initiator = template_initiator

    def load_service_values(self):
        service = self.content.get("sla_template").get("service")
        if service:
            self._service = service

    def load_license_values(self):
        license = self.content.get("sla_template").get("licenses")
        if license:
            self._license = license
class Runtime_Policy:
    def __init__(self, descriptor_file):
        self._id = None
        self._content = None
        self._filename = None
        self.filename = descriptor_file
        self._network_service = {}

    @property
    def id(self):
        return self._id
    @property
    def filename(self):
        """
        Filename of the descriptor
        :return: descriptor filename
        """
        return self._filename

    @property
    def content(self):
        """
        Content of the descriptor
        :return: descriptor content
        """
        return self._content

    @content.setter
    def content(self, content):
        """
        Sets the descriptor dictionary.
        This modification will impact the id of the descriptor.
        :param value: content, an OrderedDict
        """
        self._content = content
        self._id = descriptor_id(self._content)

    @filename.setter
    def filename(self, value):
        """
        Sets the descriptor filename.
        This modification will impact the content and id of the descriptor.
        :param value: descriptor filename
        """
        self._filename = value
        content = read_descriptor_file(self._filename)
        if content:
            self.content = content
