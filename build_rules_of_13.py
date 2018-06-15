from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser as ofp
from ryu.base import app_manager
from ryu.controller import ofp_event


class RuleCreator(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **Kwargs):
        super(RuleCreator, self).__init__()

    def add_flow(self, datapath):
        inst = self.create_actions()
        match_list = self.create_match()
        for match in match_list:
            mod = ofp.OFPFlowMod(datapath=datapath, instructions=inst)
            mod.match = match
            print(mod)
            datapath.send_msg(mod)

    def create_actions(self):
        actions_builder = Actions13Builder()
        actions = actions_builder.set_output_normal_port().set_controller_output_port().set_pop_vlan().build()
        return actions

    def create_match(self):
        """
        Create math with multiple TCP ports:
        :return: match list
        """
        mb = MatchBuilder()
        match_list = []

        match = mb.set_eth_type().set_in_port(1).set_ipv4_dst('10.1.0.1').set_ipv4_src("10.2.0.1").\
            set_vlan_vid((0x1000 | 101)).set_tcp_field(src_port=1).build()

        match_list.append(match)

        return match_list

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def get_datapath(self, ev):
        datapath = ev.msg.datapath
        self.add_flow(datapath)


class MatchBuilder:

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
        self.match_fields['ip_proto'] = 6
        if src_port is not None:
            self.match_fields['tcp_src'] = src_port
        if dst_port is not None:
            self.match_fields['tcp_dst'] = dst_port
        return self

    def set_udp_field(self, src_port=None, dst_port=None):
        self.match_fields['ip_proto'] = 17
        if src_port is not None:
            self.match_fields['udp_src'] = src_port
        if dst_port is not None:
            self.match_fields['udp_dst'] = dst_port
        return self

    def build(self):
        match = ofp.OFPMatch(**self.match_fields)
        return match


class Actions13Builder(object):

    def __init__(self):
        self.actions_fields = []

    def set_mac_rewrite(self, eth_src):
        self.actions_fields.append(ofp.OFPActionSetField(eth_src=eth_src))
        return self

    def set_vlan(self, vlan_id):
        self.actions_fields.append(ofp.OFPActionPushVlan())
        self.actions_fields.append(ofp.OFPActionSetField(vlan_vid=(0x1000 | vlan_id)))
        return self

    def set_extract_vlan(self):
        self.actions_fields.append(ofp.OFPActionPopVlan())
        return self

    def set_pop_vlan(self):
        self.actions_fields.append(ofp.OFPActionPopVlan())
        return self

    def set_output_port(self, port):
        self.actions_fields.append(ofp.OFPActionOutput(port=port))
        return self

    def set_output_normal_port(self):
        self.actions_fields.append(ofp.OFPActionOutput(ofproto_v1_3.OFPP_NORMAL))
        return self

    def set_controller_output_port(self):
        self.actions_fields.append(ofp.OFPActionOutput(ofproto_v1_3.OFPP_CONTROLLER))
        return self

    def build(self):
        return [ofp.OFPInstructionActions(ofproto_v1_3.OFPIT_APPLY_ACTIONS, self.actions_fields)]
