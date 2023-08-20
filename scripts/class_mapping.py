from http1_covered_channels import *



requests_builders ={
    1: HTTP1_Request_Builder,
    2: HTTP1_Request_CC_Case_Insensitivity,
    3: HTTP1_Request_CC_Random_Whitespace,
    4: HTTP1_Request_CC_Reordering_Header_Fields,
    5: HTTP1_Request_CC_URI_Represenation,
    6: HTTP1_Request_CC_URI_Case_Insentivity,
    7: HTTP1_Request_CC_URI_Hex_Hex,
    8: HTTP1_Request_CC_Random_Content,
    9: HTTP1_Request_CC_Random_Content_No_Lenght_Field,
    10: HTTP1_Request_CC_URI_Common_Addresses,
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