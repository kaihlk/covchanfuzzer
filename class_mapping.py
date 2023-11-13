from http1_covered_channels import *



requests_builders ={
    0: HTTP1_Request_from_CSV,
    1: HTTP1_Request_Builder,
    2: HTTP1_Request_CC_Case_Insensitivity,
    3: HTTP1_Request_CC_Random_Whitespace,
    31: HTTP1_Request_CC_Random_Whitespace_opt,
    32: HTTP1_Request_CC_Random_Whitespace_opt2,
    33: HTTP1_Request_CC_Random_Whitespace_opt3,
    34: HTTP1_Request_CC_Random_Whitespace_opt4,
    4: HTTP1_Request_CC_Reordering_Header_Fields,
    5: HTTP1_Request_CC_URI_Represenation,
    51: HTTP1_Request_CC_URI_Represenation_opt1,
    52: HTTP1_Request_CC_URI_Represenation_opt2,
    53: HTTP1_Request_CC_URI_Represenation_opt3,
    6: HTTP1_Request_CC_URI_Case_Insentivity,
    61: HTTP1_Request_CC_URI_Case_Insentivity_opt1,
    7: HTTP1_Request_CC_URI_Extend_with_fragments,
    71: HTTP1_Request_CC_URI_Extend_with_fragments_opt1,
    8: HTTP1_Request_CC_Add_Random_Header_Fields,
    9: HTTP1_Request_CC_Add_Big_Header_Field,
    #13: HTTP1_Request_CC_Add_Random_Header_Fields,
    #14: HTTP1_Request_CC_Add_Big_Header_Field,
}
    #7: HTTP1_Request_CC_URI_Hex_Hex,
    #7: HTTP1_Request_CC_URI_Extend_with_fragments,
    #71 HTTP1_Request_CC_URI_Extend_with_fragments_opt1,

    #8: HTTP1_Request_CC_Random_Content,
    #9: HTTP1_Request_CC_Random_Content_No_Lenght_Field,
    #10: HTTP1_Request_CC_URI_Common_Addresses,
    #11: HTTP1_Request_CC_URI_Common_Addresses_And_Anchors,
    #12: HTTP1_Request_CC_URI_Extend_with_fragments,
    #13: HTTP1_Request_CC_Add_Random_Header_Fields,
    #14: HTTP1_Request_CC_Add_Big_Header_Field,
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