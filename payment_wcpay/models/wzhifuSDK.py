# -*- coding: utf-8 -*-
"""
Created on 2014-11-24

@author: http://blog.csdn.net/yueguanghaidao,yihaibo@longtugame.com

 * 微信支付帮助库
 * ====================================================
 * 接口分三种类型：
 * 【请求型接口】--Wxpay_client_
 *      统一支付接口类--UnifiedOrder
 *      订单查询接口--OrderQuery
 *      退款申请接口--Refund
 *      退款查询接口--RefundQuery
 *      对账单接口--DownloadBill
 *      短链接转换接口--ShortUrl
 * 【响应型接口】--Wxpay_server_
 *      通用通知接口--Notify
 *      Native支付——请求商家获取商品信息接口--NativeCall
 * 【其他】
 *      静态链接二维码--NativeLink
 *      JSAPI支付--JsApi
 * =====================================================
 * 【CommonUtil】常用工具：
 *      trim_string()，设置参数时需要用到的字符处理函数
 *      create_noncestr()，产生随机字符串，不长于32位
 *      format_biz_query_para_map(),格式化参数，签名过程需要用到
 *      get_sign(),生成签名
 *      array_to_xml(),array转xml
 *      xml_to_array(),xml转 array
 *      post_xml_curl(),以post方式提交xml到对应的接口url
 *      post_xml_ssl_curl(),使用证书，以post方式提交xml到对应的接口url

"""

import json
import time
import random
import urllib2
import hashlib
import threading
from urllib import quote
import xml.etree.ElementTree as ET

try:
    import pycurl
    from cstringIO import stringIO
except ImportError:
    pycurl = None


class WxPayConf_pub(object):
    """配置账号信息"""

    # =======【基本信息设置】=====================================
    # 微信公众号身份的唯一标识。审核通过后，在微信发送的邮件中查看
    APPID = "wx722ad3aa4431f1e2"
    # JSAPI接口中获取openid，审核后在公众平台开启开发模式后可查看
    APPSECRET = "6ee08cfd29d5cb8ae5daca3e4ded9938"
    # 受理商ID，身份标识
    MCHID = "1263656001"
    # 商户支付密钥Key。审核通过后，在微信发送的邮件中查看
    KEY = "6ee08cfd29d5cb86ee08cfd29d5cb888"

    # =======【异步通知url设置】===================================
    # 异步通知url，商户根据实际开发过程设定
    # NOTIFY_URL = "http://******.com/payback"
    NOTIFY_URL = "https://wechat-trunk.my-odoo.com/payment/wcpay/notify"

    # =======【JSAPI路径设置】===================================
    # 获取access_token过程中的跳转uri，通过跳转将code传入jsapi支付页面
    JS_API_CALL_URL = "https://wechat-trunk.my-odoo.com/pay/?showwxpaytitle=1"

    # =======【证书路径设置】=====================================
    # 证书路径,注意应该填写绝对路径
    SSLCERT_PATH = "/******/cacert/apiclient_cert.pem"
    SSLKEY_PATH = "/******/cacert/apiclient_key.pem"

    # =======【curl超时设置】===================================
    CURL_TIMEOUT = 30

    # =======【HTTP客户端设置】===================================
    HTTP_CLIENT = "CURL"  # ("URLLIB", "CURL")


class Singleton(object):
    """单例模式"""

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    impl = cls.configure()\
                        if hasattr(cls, "configure") else cls
                    instance = super(Singleton, cls).__new__(
                        impl, *args, **kwargs)
                    if not isinstance(instance, cls):
                        instance.__init__(*args, **kwargs)
                    cls._instance = instance
        return cls._instance


class UrllibClient(object):
    """使用urlib2发送请求"""

    def get(self, url, second=30):
        return self.post_xml(None, url, second)

    def post_xml(self, xml, url, second=30):
        """不使用证书"""
        data = urllib2.urlopen(url, xml, timeout=second).read()
        return data

    def post_xml_ssl(self, xml, url, second=30):
        """使用证书"""
        raise TypeError("please use _curlClient")


class _curlClient(object):
    """使用_curl发送请求"""
    def __init__(self):
        self.curl = pycurl._curl()
        self.curl.setopt(pycurl.SSL_VERIFYHOST, False)
        self.curl.setopt(pycurl.SSL_VERIFYPEER, False)
        # 设置不输出header
        self.curl.setopt(pycurl.HEADER, False)

    def get(self, url, second=30):
        return self.post_xml_ssl(
            None, url, second=second, cert=False, post=False)

    def post_xml(self, xml, url, second=30):
        """不使用证书"""
        return self.post_xml_ssl(
            xml, url, second=second, cert=False, post=True)

    def post_xml_ssl(self, xml, url, second=30, cert=True, post=True):
        """使用证书"""
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.TIMEOUT, second)
        # 设置证书
        # 使用证书：cert 与 key 分别属于两个.pem文件
        # 默认格式为PEM，可以注释
        if cert:
            self.curl.setopt(pycurl.SSLKEYTYPE, "PEM")
            self.curl.setopt(pycurl.SSLKEY, WxPayConf_pub.SSLKEY_PATH)
            self.curl.setopt(pycurl.SSLCERTTYPE, "PEM")
            self.curl.setopt(pycurl.SSLCERT, WxPayConf_pub.SSLCERT_PATH)
        # post提交方式
        if post:
            self.curl.setopt(pycurl.POST, True)
            self.curl.setopt(pycurl.POSTFIELDS, xml)
        buff = stringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, buff.write)

        self.curl.perform()
        return buff.getvalue()


class HttpClient(Singleton):
    @classmethod
    def configure(cls):
        if pycurl is not None and WxPayConf_pub.HTTP_CLIENT != "URLLIB":
            return _curlClient
        else:
            return UrllibClient


class Common_util_pub(object):
    """所有接口的基类"""

    def trim_string(self, value):
        if value is not None and len(value) == 0:
            value = None
        return value

    def create_noncestr(self, length=32):
        """产生随机字符串，不长于32位"""
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)

    def format_biz_query_para_map(self, para_map, urlencode):
        """格式化参数，签名过程需要使用"""
        slist = sorted(para_map)
        buff = []
        for k in slist:
            v = quote(para_map[k]) if urlencode else para_map[k]
            buff.append("{0}={1}".format(k, v))

        return "&".join(buff)

    def get_sign(self, obj):
        """生成签名"""
        # 签名步骤一：按字典序排序参数,format_biz_query_para_map已做
        string = self.format_biz_query_para_map(obj, False)
        # 签名步骤二：在string后加入KEY
        string = "{0}&key={1}".format(string, WxPayConf_pub.KEY)
        # 签名步骤三：MD5加密
        string = hashlib.md5(string).hexdigest()
        # 签名步骤四：所有字符转为大写
        result_ = string.upper()
        return result_

    def array_to_xml(self, arr):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in arr.iteritems():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
        xml.append("</xml>")
        return "".join(xml)

    def xml_to_array(self, xml):
        """将xml转为array"""
        array_data = {}
        root = ET.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data

    def post_xml_curl(self, xml, url, second=30):
        """以post方式提交xml到对应的接口url"""
        return HttpClient().post_xml(xml, url, second=second)

    def post_xml_ssl_curl(self, xml, url, second=30):
        """使用证书，以post方式提交xml到对应的接口url"""
        return HttpClient().post_xml_ssl(xml, url, second=second)


class JsApi_pub(Common_util_pub):
    """JSAPI支付——H5网页端调起支付接口"""
    code = None    # code码，用以获取openid
    openid = None  # 用户的openid
    parameters = None  # jsapi参数，格式为json
    prepay_id = None  # 使用统一支付接口得到的预支付id
    curl_timeout = None  # curl超时时间

    def __init__(self, timeout=WxPayConf_pub.CURL_TIMEOUT):
        self.curl_timeout = timeout

    def create_oauth_url_for_code(self, redirect_url):
        """生成可以获得code的url"""
        url_obj = {}
        url_obj["appid"] = WxPayConf_pub.APPID
        url_obj["redirect_uri"] = redirect_url
        url_obj["response_type"] = "code"
        url_obj["scope"] = "snsapi_base"
        url_obj["state"] = "STATE#wechat_redirect"
        bizstring = self.format_biz_query_para_map(url_obj, False)
        return "https://open.weixin.qq.com/connect/oauth2/authorize?"\
            + bizstring

    def create_oauth_url_for_openid(self):
        """生成可以获得openid的url"""
        url_obj = {}
        url_obj["appid"] = WxPayConf_pub.APPID
        url_obj["secret"] = WxPayConf_pub.APPSECRET
        url_obj["code"] = self.code
        url_obj["grant_type"] = "authorization_code"
        bizstring = self.format_biz_query_para_map(url_obj, False)
        return "https://api.weixin.qq.com/sns/oauth2/access_token?" + bizstring

    def get_openid(self):
        """通过curl向微信提交code，以获取openid"""
        url = self.create_oauth_url_for_openid()
        data = HttpClient().get(url)
        self.openid = json.loads(data)["openid"]
        return self.openid

    def set_prepay_id(self, prepay_id):
        """设置prepay_id"""
        self.prepay_id = prepay_id

    def set_code(self, code):
        """设置code"""
        self.code = code

    def get_parameters(self):
        """设置jsapi的参数"""
        js_api_obj = {}
        js_api_obj["appId"] = WxPayConf_pub.APPID
        time_stamp = int(time.time())
        js_api_obj["timeStamp"] = "{0}".format(time_stamp)
        js_api_obj["nonceStr"] = self.create_noncestr()
        js_api_obj["package"] = "prepay_id={0}".format(self.prepay_id)
        js_api_obj["signType"] = "MD5"
        js_api_obj["paySign"] = self.get_sign(js_api_obj)
        self.parameters = json.dumps(js_api_obj)

        return self.parameters


class Wxpay_client_pub(Common_util_pub):
    """请求型接口的基类"""
    response = None  # s微信返回的响应
    url = None  # 接口链接
    curl_timeout = None  # curl超时时间

    def __init__(self):
        self.parameters = {}  # 请求参数，类型为关联数组
        self.result = {}     # 返回参数，类型为关联数组

    def set_parameters(self, parameter, parameter_value):
        """设置请求参数"""
        self.parameters[self.trim_string(parameter)] =\
            self.trim_string(parameter_value)

    def create_xml(self):
        """设置标配的请求参数，生成签名，生成接口参数xml"""
        self.parameters["appid"] = WxPayConf_pub.APPID   # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID   # 商户号
        self.parameters["nonce_str"] = self.create_noncestr()   # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)   # 签名
        return self.array_to_xml(self.parameters)

    def post_xml(self):
        """post请求xml"""
        xml = self.create_xml()
        self.response = self.post_xml_curl(xml, self.url, self.curl_timeout)
        return self.response

    def post_xml_ssl(self):
        """使用证书post请求xml"""
        xml = self.create_xml()
        self.response = self.post_xml_ssl_curl(
            xml, self.url, self.curl_timeout)
        return self.response

    def get_result(self):
        """获取结果，默认不使用证书"""
        self.post_xml()
        self.result = self.xml_to_array(self.response)
        return self.result


class UnifiedOrder_pub(Wxpay_client_pub):
    """统一支付接口类"""

    def __init__(self, timeout=WxPayConf_pub.CURL_TIMEOUT):
        # 设置接口链接
        self.url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
        # 设置curl超时时间
        self.curl_timeout = timeout
        super(UnifiedOrder_pub, self).__init__()

    def create_xml(self):
        """生成接口参数xml"""
        # 检测必填参数
        if any(self.parameters[key] is None for key in (
                "out_trade_no", "body", "total_fee",
                "notify_url", "trade_type")):
            raise ValueError("missing parameter")
        if self.parameters["trade_type"] == "JSAPI"\
                and self.parameters["openid"] is None:
            raise ValueError("JSAPI need openid parameters")

        self.parameters["appid"] = WxPayConf_pub.APPID  # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
        self.parameters["spbill_create_ip"] = '192.168.2.255'  # "127.0.0.1"
        self.parameters["nonce_str"] = self.create_noncestr()  # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)  # 签名
        return self.array_to_xml(self.parameters)

    def get_prepay_id(self):
        """获取prepay_id"""
        self.post_xml()
        self.result = self.xml_to_array(self.response)
        prepay_id = self.result["prepay_id"]
        return prepay_id


class OrderQuery_pub(Wxpay_client_pub):
    """订单查询接口"""

    def __init__(self, timeout=WxPayConf_pub.CURL_TIMEOUT):
        # 设置接口链接
        self.url = "https://api.mch.weixin.qq.com/pay/orderquery"
        # 设置curl超时时间
        self.curl_timeout = timeout
        super(OrderQuery_pub, self).__init__()

    def create_xml(self):
        """生成接口参数xml"""

        # 检测必填参数
        if any(self.parameters[key] is None
                for key in ("out_trade_no", "transaction_id")):
            raise ValueError("missing parameter")

        self.parameters["appid"] = WxPayConf_pub.APPID  # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
        self.parameters["nonce_str"] = self.create_noncestr()  # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)  # 签名
        return self.array_to_xml(self.parameters)


class Refund_pub(Wxpay_client_pub):
    """退款申请接口"""

    def __init__(self, timeout=WxPayConf_pub.CURL_TIMEOUT):
        # 设置接口链接
        self.url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
        # 设置curl超时时间
        self.curl_timeout = timeout
        super(Refund_pub, self).__init__()

    def create_xml(self):
        """生成接口参数xml"""
        if any(self.parameters[key] is None
                for key in (
                    "out_trade_no", "out_refund_no", "total_fee",
                    "refund_fee", "op_user_id")):
            raise ValueError("missing parameter")

        self.parameters["appid"] = WxPayConf_pub.APPID  # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
        self.parameters["nonce_str"] = self.create_noncestr()  # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)  # 签名
        return self.array_to_xml(self.parameters)

    def get_result(self):
        """ 获取结果，使用证书通信(需要双向证书)"""
        self.post_xml_ssl()
        self.result = self.xml_to_array(self.response)
        return self.result


class RefundQuery_pub(Wxpay_client_pub):
    """退款查询接口"""

    def __init__(self, timeout=WxPayConf_pub.CURL_TIMEOUT):
        # 设置接口链接
        self.url = "https://api.mch.weixin.qq.com/pay/refundquery"
        # 设置curl超时时间
        self.curl_timeout = timeout
        super(RefundQuery_pub, self).__init__()

    def create_xml(self):
        """生成接口参数xml"""
        if any(
            self.parameters[key] is None for key in
            ("out_refund_no", "out_trade_no",
                "transaction_id", "refund_id")):
            raise ValueError("missing parameter")
        self.parameters["appid"] = WxPayConf_pub.APPID  # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
        self.parameters["nonce_str"] = self.create_noncestr()  # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)  # 签名
        return self.array_to_xml(self.parameters)

    def get_result(self):
        """ 获取结果，使用证书通信(需要双向证书)"""
        self.post_xml_ssl()
        self.result = self.xml_to_array(self.response)
        return self.result


class DownloadBill_pub(Wxpay_client_pub):
    """对账单接口"""

    def __init__(self, timeout=WxPayConf_pub.CURL_TIMEOUT):
        # 设置接口链接
        self.url = "https://api.mch.weixin.qq.com/pay/downloadbill"
        # 设置curl超时时间
        self.curl_timeout = timeout
        super(DownloadBill_pub, self).__init__()

    def create_xml(self):
        """生成接口参数xml"""
        if any(self.parameters[key] is None for key in ("bill_date", )):
            raise ValueError("missing parameter")

        self.parameters["appid"] = WxPayConf_pub.APPID  # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
        self.parameters["nonce_str"] = self.create_noncestr()  # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)  # 签名
        return self.array_to_xml(self.parameters)

    def get_result(self):
        """获取结果，默认不使用证书"""
        self.post_xml()
        self.result = self.xml_to_array(self.response)
        return self.result


class ShortUrl_pub(Wxpay_client_pub):
    """短链接转换接口"""

    def __init__(self, timeout=WxPayConf_pub.CURL_TIMEOUT):
        # 设置接口链接
        self.url = "https://api.mch.weixin.qq.com/tools/shorturl"
        # 设置curl超时时间
        self.curl_timeout = timeout
        super(ShortUrl_pub, self).__init__()

    def create_xml(self):
        """生成接口参数xml"""
        if any(self.parameters[key] is None for key in ("long_url", )):
            raise ValueError("missing parameter")

        self.parameters["appid"] = WxPayConf_pub.APPID  # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
        self.parameters["nonce_str"] = self.create_noncestr()  # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)  # 签名
        return self.array_to_xml(self.parameters)

    def get_short_url(self):
        """获取prepay_id"""
        self.post_xml()
        prepay_id = self.result["short_url"]
        return prepay_id


class Wxpay_server_pub(Common_util_pub):
    """响应型接口基类"""
    SUCCESS, FAIL = "SUCCESS", "FAIL"

    def __init__(self):
        self.data = {}  # 接收到的数据，类型为关联数组
        self.returnParameters = {}  # 返回参数，类型为关联数组

    def save_data(self, xml):
        """将微信的请求xml转换成关联数组，以方便数据处理"""
        self.data = self.xml_to_array(xml)

    def check_sign(self):
        """校验签名"""
        tmp_data = dict(self.data)   # a copy to save sign
        del tmp_data['sign']
        sign = self.get_sign(tmp_data)  # 本地签名
        if self.data['sign'] == sign:
            return True
        return False

    def get_data(self):
        """获取微信的请求数据"""
        return self.data

    def set_return_parameter(self, parameter, parameter_value):
        """设置返回微信的xml数据"""
        self.returnParameters[self.trim_string(parameter)] = self.trim_string(
            parameter_value)

    def create_xml(self):
        """生成接口参数xml"""
        return self.array_to_xml(self.returnParameters)

    def return_xml(self):
        """将xml数据返回微信"""
        return_xml = self.create_xml()
        return return_xml


class Notify_pub(Wxpay_server_pub):
    """通用通知接口"""


class NativeCall_pub(Wxpay_server_pub):
    """请求商家获取商品信息接口"""

    def create_xml(self):
        """生成接口参数xml"""
        if self.returnParameters["return_code"] == self.SUCCESS:
            self.returnParameters["appid"] = WxPayConf_pub.APPID  # 公众账号ID
            self.returnParameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
            self.returnParameters["nonce_str"] = self.create_noncestr()
            self.returnParameters["sign"] = self.get_sign(
                self.returnParameters)
        return self.array_to_xml(self.returnParameters)

    def get_product_id(self):
        """获取product_id"""
        product_id = self.data["product_id"]
        return product_id


class NativeLink_pub(Common_util_pub):
    """静态链接二维码"""

    url = None  # 静态链接

    def __init__(self):
        self.parameters = {}  # 静态链接参数

    def set_parameters(self, parameter, parameter_value):
        """设置参数"""
        self.parameters[self.trim_string(parameter)] = self.trim_string(
            parameter_value)

    def create_link(self):
        if any(self.parameters[key] is None for key in ("product_id", )):
            raise ValueError("missing parameter")

        self.parameters["appid"] = WxPayConf_pub.APPID   # 公众账号ID
        self.parameters["mch_id"] = WxPayConf_pub.MCHID  # 商户号
        time_stamp = int(time.time())
        self.parameters["time_stamp"] = "{0}".format(time_stamp)  # 时间戳
        self.parameters["nonce_str"] = self.create_noncestr()  # 随机字符串
        self.parameters["sign"] = self.get_sign(self.parameters)  # 签名
        bizstring = self.format_biz_query_para_map(self.parameters, False)
        self.url = "weixin://wxpay/bizpayurl?" + bizstring

    def get_url(self):
        """返回链接"""
        self.create_link()
        return self.url


def test():
    c = HttpClient()
    assert c.get("http://www.baidu.com")[:15] == "<!DOCTYPE html>"
    c2 = HttpClient()
    assert id(c) == id(c2)


if __name__ == "__main__":
    test()
