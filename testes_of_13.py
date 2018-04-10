from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser as ofp
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.topology import event
import copy

class RuleCreator(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **Kwargs):
        super(RuleCreator, self).__init__()

    def add_flow(self, datapath):
        inst = [ofp.OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS, self.create_actions())]
        match_list = self.create_match()
        for match in match_list:
            print(match)
            mod = ofp.OFPFlowMod(datapath=datapath, match=match, instructions=inst)
            datapath.send_msg(mod)

    def create_match(self):
        mb = MatchBuilder()
        match_list = []

        ports = [1,2,3]
        match = mb.set_in_port(1).set_eth_type().set_vlan_vid((0x1000 | 101))

        for p in ports:
            match_copy = match
            match_copy = match_copy.set_tcp_field(src_port=p).build()
            match_list.append(match_copy)

        return match_list

    def create_actions(self):
        actions = [ofp.OFPActionOutput(port=3)]
        return  actions

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def get_datapath(self, ev):
        datapath = ev.msg.datapath
        self.add_flow(datapath)

class MatchBuilder():

    def __init__(self):
        self.match_fields = {}

    def set_eth_type(self, eth_type=0x800):
        self.match_fields['eth_type'] = eth_type
        return self

    def set_ipv4_src(self, ipv4_src, ipv4_src_mask='32'):
        mask = '255.255.255.255'
        if ipv4_src_mask == '24':
            mask = '255.255.255.0'
        self.match_fields['ipv4_src'] = (ipv4_src, mask)
        return self

    def set_ipv4_dst(self, ipv4_dst, ipv4_dst_mask='32'):
        mask = '255.255.255.255'
        if ipv4_dst_mask == '24':
            mask = '255.255.255.0'
        self.match_fields['ipv4_src'] = (ipv4_dst, mask)
        return self

    def set_in_port(self, in_port):
        self.match_fields['in_port'] = in_port
        return self

    def set_vlan_vid(self, vlan_id):
        self.match_fields['vlan_vid'] = vlan_id
        return self

    def set_src_port(self, src_port):
        self.match_fields['src_port'] = src_port
        return self

    def set_dst_port(self, dst_port):
        self.match_fields['dst_port'] = dst_port
        return self

    def set_tcp_field(self, src_port=None, dst_port=None):
        self.match_fields['ip_proto']= 6
        if src_port is not None:
            self.match_fields['tcp_src'] = src_port
        if dst_port is not None:
            self.match_fields['tcp_dst'] = dst_port
        return self

    def build(self):
        match = ofp.OFPMatch(**self.match_fields)
        return match


