from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser as ofp
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.topology import event

class RuleCreator(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **Kwargs):
        super(RuleCreator, self).__init__()

    def add_flow(self, datapath):
        inst = [ofp.OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS, self.create_actions())]
        match = self.create_match()
        mod = ofp.OFPFlowMod(datapath=datapath, match=match, instructions=inst)
        datapath.send_msg(mod)

    def create_match(self):
        mb = Match_builder()
        mb.set_in_port(10)
        mb.set_eth_type(0x800)
        mb.set_ipv4_src('192.168.0.1')
        mb.set_ipv4_src_mask('32')
        mb.set_ipv4_dst('192.168.0.2')
        mb.set_ipv4_dst_mask('24')
        mb.set_vlan_vid(100)

        match = mb.build_normal()
        return match

    def create_actions(self):
        actions = [ofp.OFPActionOutput(port=10)]
        return  actions

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def get_datapath(self, ev):
        datapath = ev.msg.datapath
        self.add_flow(datapath)

class Match_builder():

    def __init__(self):
        self.eth_type = None
        self.ipv4_src = None
        self.ipv4_dst = None
        self.in_port  = None
        self.vlan_id  = None
        self.ipv4_src_mask = None
        self.ipv4_dst_mask = None

        self.src_port = None
        self.dst_port = None

    def build(self):
        pass

    def set_eth_type(self, eth_type):
        self.eth_type = eth_type

    def set_ipv4_src(self, ipv4_src):
        self.ipv4_src = ipv4_src

    def set_ipv4_dst(self, ipv4_dst):
        self.ipv4_dst = ipv4_dst

    def set_in_port(self, in_port):
        self.in_port = in_port

    def set_vlan_vid(self, vlan_id):
        self.vlan_id = vlan_id

    def set_src_port(self, src_port):
        self.src_port = src_port

    def set_dst_port(self, dst_port):
        self.dst_port = dst_port

    def set_ipv4_src_mask(self, ipv4_mask):
        if ipv4_mask == '32':
            self.ipv4_src_mask = '255.255.255.255'
        elif ipv4_mask == '24':
            self.ipv4_src_mask = '255.255.255.0'

    def set_ipv4_dst_mask(self, ipv4_mask):
        if ipv4_mask == '32':
            self.ipv4_dst_mask = '255.255.255.255'
        elif ipv4_mask == '24':
            self.ipv4_dst_mask = '255.255.255.0'

    def build_normal(self):

        match = ofp.OFPMatch(eth_type=self.eth_type,
                             ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                             ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                             in_port=self.in_port,
                             vlan_vid=self.vlan_id)
        return match

    def build_icmp(self):
        ip_proto = 1
        match = ofp.OFPMatch(eth_type=self.eth_type,
                             ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                             ipv4_src= (self.ipv4_src, self.ipv4_src_mask),
                             in_port=self.in_port,
                             vlan_vid=self.vlan_id,
                             ip_proto=ip_proto)
        return match

    def build_tcp(self):
        ip_proto = 6
        if self.src_port is not None and self.dst_port is not None:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 tcp_src= self.src_port,
                                 tcp_dst=self.dst_port,
                                 ip_proto=ip_proto)

        elif self.src_port is not None:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 tcp_src=self.src_port,
                                 ip_proto=ip_proto)
        elif self.dst_port is not None:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 tcp_dst=self.src_port,
                                 ip_proto=ip_proto)
        else:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 ip_proto=ip_proto)
        return match

    def build_upd_port(self):
        ip_proto = 17
        if self.src_port is not None and self.dst_port is not None:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 udp_src=self.src_port,
                                 udp_dst=self.dst_port,
                                 ip_proto=ip_proto)
        elif self.src_port is not None:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 udp_src=self.src_port,
                                 ip_proto=ip_proto)
        elif self.dst_port is not None:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 udp_dst=self.src_port,
                                 ip_proto=ip_proto)
        else:
            match = ofp.OFPMatch(eth_type=self.eth_type,
                                 ipv4_dst=(self.ipv4_dst, self.ipv4_dst_mask),
                                 ipv4_src=(self.ipv4_src, self.ipv4_src_mask),
                                 in_port=self.in_port,
                                 vlan_vid=self.vlan_id,
                                 ip_proto=ip_proto)
        return match