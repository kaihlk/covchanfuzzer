from http1_covered_channels import *



requests_builders ={
    0: HTTP1_Request_from_CSV,
    1: HTTP1_Request_Builder,
    2: HTTP1_Request_CC_Case_Insensitivity,
    3: HTTP1_Request_CC_Random_Whitespace,
    31: HTTP1_Request_CC_Random_Whitespace_opt,
    32: HTTP1_Request_CC_Random_Whitespace_opt2,
    4: HTTP1_Request_CC_Reordering_Header_Fields,
    5: HTTP1_Request_CC_URI_Represenation,
    51: HTTP1_Request_CC_URI_Represenation_opt,
    6: HTTP1_Request_CC_URI_Case_Insentivity,
    7: HTTP1_Request_CC_URI_Hex_Hex,
    8: HTTP1_Request_CC_Random_Content,
    9: HTTP1_Request_CC_Random_Content_No_Lenght_Field,
    10: HTTP1_Request_CC_URI_Common_Addresses,
    11: HTTP1_Request_CC_URI_Common_Addresses_And_Anchors,
    12: HTTP1_Request_CC_URI_Extend_with_fragments

}

""" class_mapping_connection = {
    1: HTTP1_TCP_Connection,
  #  2: HTTP1_TLS_Connection,
  #  3: HTTP1_CC_TCP2TLS_Upgrade,
  #  4: HTTP2_TLS_Connection
    }

class_mapping_timing  = {
  #  1: Standard,
  #  2: Frequency_Modulation,
  #  3: Amplitude_Modulation,
} """