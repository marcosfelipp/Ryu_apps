from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0 as of
from ryu.ofproto import ofproto_v1_0_parser as ofp

class L2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [of.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)
        print("ok")

    def add_flow(self, datapath):
        match = self.create_match()
        actions = self.create_actions()
        req = ofp.OFPFlowMod(
        datapath, match, 0, of.OFPFC_ADD, 0, 0, 32768, 0xffffffff, of.OFPP_NONE, 0, actions)

        datapath.send_msg(req)

    def create_match(self):
        wildcards = of.OFPFW_ALL
        wildcards = wildcards & ~of.OFPFW_DL_TYPE

        match               = ofp.OFPMatch()
        match.in_port 		= 10
        match.dl_type 		= 0x800
        match.nw_src        = "10.16.1.0"
        match.nw_dst        = "10.16.1.2"
        match.nw_src_mask   = 24
        match.nw_dst_mask   = 24

        wildcards = wildcards & ~(of.OFPFW_NW_SRC_MASK | of.OFPFW_NW_DST_MASK | of.OFPFW_IN_PORT)
        match.wildcards = wildcards
        return match

    def create_actions(self):
        actions = [ofp.OFPActionOutput(port=3)]
        return actions

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def get_datapath(self, ev):
        datapath = ev.msg.datapath
        self.add_flow(datapath)
