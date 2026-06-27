import socket

import threading

import sys

import os

import json

import urllib.parse

import hashlib

import time

import gzip

import mimetypes

import traceback

import queue

import re

from datetime import datetime, timezone

from enum import Enum



class HTTPStatus(Enum):

    CONTINUE = (100, "Continue")

    SWITCHING_PROTOCOLS = (101, "Switching Protocols")

    PROCESSING = (102, "Processing")

    OK = (200, "OK")

    CREATED = (201, "Created")

    ACCEPTED = (202, "Accepted")

    NON_AUTHORITATIVE_INFORMATION = (203, "Non-Authoritative Information")

    NO_CONTENT = (204, "No Content")

    RESET_CONTENT = (205, "Reset Content")

    PARTIAL_CONTENT = (206, "Partial Content")

    MULTI_STATUS = (207, "Multi-Status")

    ALREADY_REPORTED = (208, "Already Reported")

    IM_USED = (226, "IM Used")

    MULTIPLE_CHOICES = (300, "Multiple Choices")

    MOVED_PERMANENTLY = (301, "Moved Permanently")

    FOUND = (302, "Found")

    SEE_OTHER = (303, "See Other")

    NOT_MODIFIED = (304, "Not Modified")

    USE_PROXY = (305, "Use Proxy")

    TEMPORARY_REDIRECT = (307, "Temporary Redirect")

    PERMANENT_REDIRECT = (308, "Permanent Redirect")

    BAD_REQUEST = (400, "Bad Request")

    UNAUTHORIZED = (401, "Unauthorized")

    PAYMENT_REQUIRED = (402, "Payment Required")

    FORBIDDEN = (403, "Forbidden")

    NOT_FOUND = (404, "Not Found")

    METHOD_NOT_ALLOWED = (405, "Method Not Allowed")

    NOT_ACCEPTABLE = (406, "Not Acceptable")

    PROXY_AUTHENTICATION_REQUIRED = (407, "Proxy Authentication Required")

    REQUEST_TIMEOUT = (408, "Request Timeout")

    CONFLICT = (409, "Conflict")

    GONE = (410, "Gone")

    LENGTH_REQUIRED = (411, "Length Required")

    PRECONDITION_FAILED = (412, "Precondition Failed")

    PAYLOAD_TOO_LARGE = (413, "Payload Too Large")

    URI_TOO_LONG = (414, "URI Too Long")

    UNSUPPORTED_MEDIA_TYPE = (415, "Unsupported Media Type")

    RANGE_NOT_SATISFIABLE = (416, "Range Not Satisfiable")

    EXPECTATION_FAILED = (417, "Expectation Failed")

    IM_A_TEAPOT = (418, "I'm a teapot")

    MISDIRECTED_REQUEST = (421, "Misdirected Request")

    UNPROCESSABLE_ENTITY = (422, "Unprocessable Entity")

    LOCKED = (423, "Locked")

    FAILED_DEPENDENCY = (424, "Failed Dependency")

    TOO_EARLY = (425, "Too Early")

    UPGRADE_REQUIRED = (426, "Upgrade Required")

    PRECONDITION_REQUIRED = (428, "Precondition Required")

    TOO_MANY_REQUESTS = (429, "Too Many Requests")

    REQUEST_HEADER_FIELDS_TOO_LARGE = (431, "Request Header Fields Too Large")

    UNAVAILABLE_FOR_LEGAL_REASONS = (451, "Unavailable For Legal Reasons")

    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")

    NOT_IMPLEMENTED = (501, "Not Implemented")

    BAD_GATEWAY = (502, "Bad Gateway")

    SERVICE_UNAVAILABLE = (503, "Service Unavailable")

    GATEWAY_TIMEOUT = (504, "Gateway Timeout")

    HTTP_VERSION_NOT_SUPPORTED = (505, "HTTP Version Not Supported")

    VARIANT_ALSO_NEGOTIATES = (506, "Variant Also Negotiates")

    INSUFFICIENT_STORAGE = (507, "Insufficient Storage")

    LOOP_DETECTED = (508, "Loop Detected")

    NOT_EXTENDED = (510, "Not Extended")

    NETWORK_AUTHENTICATION_REQUIRED = (511, "Network Authentication Required")



    def __init__(self, code, phrase):

        self.code = code

        self.phrase = phrase



class HTTPException(Exception):

    def __init__(self, status, detail=None, headers=None):

        super().__init__(detail or status.phrase)

        self.status = status

        self.detail = detail

        self.headers = headers or {}



class BadRequestException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.BAD_REQUEST, detail)



class UnauthorizedException(HTTPException):

    def __init__(self, detail=None, headers=None):

        super().__init__(HTTPStatus.UNAUTHORIZED, detail, headers)



class ForbiddenException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.FORBIDDEN, detail)



class NotFoundException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.NOT_FOUND, detail)



class MethodNotAllowedException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.METHOD_NOT_ALLOWED, detail)



class RequestTimeoutException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.REQUEST_TIMEOUT, detail)



class PayloadTooLargeException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.PAYLOAD_TOO_LARGE, detail)



class UnsupportedMediaTypeException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail)



class RangeNotSatisfiableException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.RANGE_NOT_SATISFIABLE, detail)



class TooManyRequestsException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.TOO_MANY_REQUESTS, detail)



class InternalServerErrorException(HTTPException):

    def __init__(self, detail=None):

        super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, detail)



class MimeDatabase:

    _db = {

        "html": "text/html", "htm": "text/html", "shtml": "text/html", "css": "text/css",

        "xml": "text/xml", "gif": "image/gif", "jpeg": "image/jpeg", "jpg": "image/jpeg",

        "js": "application/javascript", "atom": "application/atom+xml", "rss": "application/rss+xml",

        "mml": "text/mathml", "txt": "text/plain", "jad": "text/vnd.sun.j2me.app-descriptor",

        "wml": "text/vnd.wap.wml", "htc": "text/x-component", "png": "image/png",

        "svg": "image/svg+xml", "svgz": "image/svg+xml", "tif": "image/tiff",

        "tiff": "image/tiff", "wbmp": "image/vnd.wap.wbmp", "webp": "image/webp",

        "ico": "image/x-icon", "jng": "image/x-jng", "bmp": "image/x-ms-bmp",

        "woff": "font/woff", "woff2": "font/woff2", "jar": "application/java-archive",

        "war": "application/java-archive", "ear": "application/java-archive", "json": "application/json",

        "hqx": "application/mac-binhex40", "doc": "application/msword", "pdf": "application/pdf",

        "ps": "application/postscript", "eps": "application/postscript", "ai": "application/postscript",

        "rtf": "application/rtf", "m3u8": "application/vnd.apple.mpegurl", "kml": "application/vnd.google-earth.kml+xml",

        "kmz": "application/vnd.google-earth.kmz", "xls": "application/vnd.ms-excel",

        "eot": "application/vnd.ms-fontobject", "ppt": "application/vnd.ms-powerpoint",

        "odg": "application/vnd.oasis.opendocument.graphics", "odp": "application/vnd.oasis.opendocument.presentation",

        "ods": "application/vnd.oasis.opendocument.spreadsheet", "odt": "application/vnd.oasis.opendocument.text",

        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

        "wmlc": "application/vnd.wap.wmlc", "7z": "application/x-7z-compressed",

        "cco": "application/x-cocoa", "jardiff": "application/x-java-archive-diff",

        "jnlp": "application/x-java-jnlp-file", "run": "application/x-makeself",

        "pl": "application/x-perl", "pm": "application/x-perl", "prc": "application/x-pilot",

        "pdb": "application/x-pilot", "rar": "application/x-rar-compressed",

        "rpm": "application/x-redhat-package-manager", "sea": "application/x-sea",

        "swf": "application/x-shockwave-flash", "sit": "application/x-stuffit",

        "tcl": "application/x-tcl", "tk": "application/x-tcl", "der": "application/x-x509-ca-cert",

        "pem": "application/x-x509-ca-cert", "crt": "application/x-x509-ca-cert",

        "xpi": "application/x-xpinstall", "xhtml": "application/xhtml+xml",

        "xspf": "application/xspf+xml", "zip": "application/zip", "bin": "application/octet-stream",

        "exe": "application/octet-stream", "dll": "application/octet-stream",

        "deb": "application/octet-stream", "dmg": "application/octet-stream",

        "iso": "application/octet-stream", "img": "application/octet-stream",

        "msi": "application/octet-stream", "msp": "application/octet-stream",

        "msm": "application/octet-stream", "mid": "audio/midi", "midi": "audio/midi",

        "kar": "audio/midi", "mp3": "audio/mpeg", "ogg": "audio/ogg", "m4a": "audio/x-m4a",

        "ra": "audio/x-realaudio", "3gpp": "video/3gpp", "3gp": "video/3gpp",

        "ts": "video/mp2t", "mp4": "video/mp4", "mpeg": "video/mpeg", "mpg": "video/mpeg",

        "mov": "video/quicktime", "webm": "video/webm", "flv": "video/x-flv",

        "m4v": "video/x-m4v", "mng": "video/x-mng", "asx": "video/x-ms-asf",

        "asf": "video/x-ms-asf", "wmv": "video/x-ms-wmv", "avi": "video/x-msvideo"

    }



    @classmethod

    def get(cls, filename, default="application/octet-stream"):

        ext = filename.split(".")[-1].lower() if "." in filename else ""

        return cls._db.get(ext, default)



class CaseInsensitiveDict:

    def __init__(self, data=None):

        self._store = {}

        if data:

            for k, v in data.items():

                self[k] = v



    def __setitem__(self, key, value):

        self._store[key.lower()] = (key, value)



    def __getitem__(self, key):

        return self._store[key.lower()][1]



    def __delitem__(self, key):

        del self._store[key.lower()]



    def __contains__(self, key):

        return key.lower() in self._store



    def get(self, key, default=None):

        try:

            return self[key]

        except KeyError:

            return default



    def items(self):

        return [item for item in self._store.values()]



    def keys(self):

        return [item[0] for item in self._store.values()]



    def values(self):

        return [item[1] for item in self._store.values()]





class SimplePBKDF2:

    @staticmethod

    def hash_password(password, salt=None):

        if not salt:

            salt = os.urandom(16).hex()

        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)

        return f"pbkdf2_sha256$100000${salt}${dk.hex()}"

        

    @staticmethod

    def verify_password(password, hash_str):

        parts = hash_str.split("$")

        if len(parts) != 4:

            return False

        _, iterations, salt, key_hex = parts

        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(iterations))

        return dk.hex() == key_hex



class CSVExporter:

    @staticmethod

    def export_feedbacks(feedbacks):

        lines = ["teacher_id,rating_pc,comment"]

        for fb in feedbacks:

            comment = fb['comment'].replace('"', '""')

            lines.append(f"{fb['teacher_id']},{fb['rating_pc']},\"{comment}\"")

        return "\n".join(lines)



class ExpandedMimeDatabase:

    _db = {

        "html": "text/html", "htm": "text/html", "shtml": "text/html", "css": "text/css",

        "xml": "text/xml", "gif": "image/gif", "jpeg": "image/jpeg", "jpg": "image/jpeg",

        "js": "application/javascript", "atom": "application/atom+xml", "rss": "application/rss+xml",

        "mml": "text/mathml", "txt": "text/plain", "jad": "text/vnd.sun.j2me.app-descriptor",

        "wml": "text/vnd.wap.wml", "htc": "text/x-component", "png": "image/png",

        "svg": "image/svg+xml", "svgz": "image/svg+xml", "tif": "image/tiff",

        "tiff": "image/tiff", "wbmp": "image/vnd.wap.wbmp", "webp": "image/webp",

        "ico": "image/x-icon", "jng": "image/x-jng", "bmp": "image/x-ms-bmp",

        "woff": "font/woff", "woff2": "font/woff2", "jar": "application/java-archive",

        "war": "application/java-archive", "ear": "application/java-archive", "json": "application/json",

        "hqx": "application/mac-binhex40", "doc": "application/msword", "pdf": "application/pdf",

        "ps": "application/postscript", "eps": "application/postscript", "ai": "application/postscript",

        "rtf": "application/rtf", "m3u8": "application/vnd.apple.mpegurl", "kml": "application/vnd.google-earth.kml+xml",

        "kmz": "application/vnd.google-earth.kmz", "xls": "application/vnd.ms-excel",

        "eot": "application/vnd.ms-fontobject", "ppt": "application/vnd.ms-powerpoint",

        "odg": "application/vnd.oasis.opendocument.graphics", "odp": "application/vnd.oasis.opendocument.presentation",

        "ods": "application/vnd.oasis.opendocument.spreadsheet", "odt": "application/vnd.oasis.opendocument.text",

        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

        "wmlc": "application/vnd.wap.wmlc", "7z": "application/x-7z-compressed",

        "cco": "application/x-cocoa", "jardiff": "application/x-java-archive-diff",

        "jnlp": "application/x-java-jnlp-file", "run": "application/x-makeself",

        "pl": "application/x-perl", "pm": "application/x-perl", "prc": "application/x-pilot",

        "pdb": "application/x-pilot", "rar": "application/x-rar-compressed",

        "rpm": "application/x-redhat-package-manager", "sea": "application/x-sea",

        "swf": "application/x-shockwave-flash", "sit": "application/x-stuffit",

        "tcl": "application/x-tcl", "tk": "application/x-tcl", "der": "application/x-x509-ca-cert",

        "pem": "application/x-x509-ca-cert", "crt": "application/x-x509-ca-cert",

        "xpi": "application/x-xpinstall", "xhtml": "application/xhtml+xml",

        "xspf": "application/xspf+xml", "zip": "application/zip", "bin": "application/octet-stream",

        "exe": "application/octet-stream", "dll": "application/octet-stream",

        "deb": "application/octet-stream", "dmg": "application/octet-stream",

        "iso": "application/octet-stream", "img": "application/octet-stream",

        "msi": "application/octet-stream", "msp": "application/octet-stream",

        "msm": "application/octet-stream", "mid": "audio/midi", "midi": "audio/midi",

        "kar": "audio/midi", "mp3": "audio/mpeg", "ogg": "audio/ogg", "m4a": "audio/x-m4a",

        "ra": "audio/x-realaudio", "3gpp": "video/3gpp", "3gp": "video/3gpp",

        "ts": "video/mp2t", "mp4": "video/mp4", "mpeg": "video/mpeg", "mpg": "video/mpeg",

        "mov": "video/quicktime", "webm": "video/webm", "flv": "video/x-flv",

        "m4v": "video/x-m4v", "mng": "video/x-mng", "asx": "video/x-ms-asf",

        "asf": "video/x-ms-asf", "wmv": "video/x-ms-wmv", "avi": "video/x-msvideo",

        "mpga": "audio/mpeg", "mp4a": "audio/mp4", "wav": "audio/wav", "weba": "audio/webm",

        "oga": "audio/ogg", "spx": "audio/ogg", "flac": "audio/flac", "m4b": "audio/mp4",

        "sfnt": "font/sfnt", "ttf": "font/ttf", "otf": "font/otf", "svgt": "image/svg+xml",

        "gpx": "application/gpx+xml", "epub": "application/epub+zip", "apk": "application/vnd.android.package-archive",

        "torrent": "application/x-bittorrent", "key": "application/x-iwork-keynote-sffkey",

        "numbers": "application/x-iwork-numbers-sffnumbers", "pages": "application/x-iwork-pages-sffpages"

    }



    @classmethod

    def get(cls, filename, default="application/octet-stream"):

        ext = filename.split(".")[-1].lower() if "." in filename else ""

        return cls._db.get(ext, default)





class Cookie:

    def __init__(self, name, value, max_age=None, path="/", domain=None, secure=False, httponly=False, samesite=None):

        self.name = name

        self.value = value

        self.max_age = max_age

        self.path = path

        self.domain = domain

        self.secure = secure

        self.httponly = httponly

        self.samesite = samesite



    def serialize(self):

        parts = [f"{self.name}={urllib.parse.quote(self.value)}"]

        if self.max_age is not None:

            parts.append(f"Max-Age={self.max_age}")

        if self.path:

            parts.append(f"Path={self.path}")

        if self.domain:

            parts.append(f"Domain={self.domain}")

        if self.secure:

            parts.append("Secure")

        if self.httponly:

            parts.append("HttpOnly")

        if self.samesite:

            parts.append(f"SameSite={self.samesite}")

        return "; ".join(parts)



class CookieJar:

    def __init__(self):

        self._cookies = {}



    def add(self, cookie):

        self._cookies[cookie.name] = cookie



    def get(self, name):

        return self._cookies.get(name)



    def values(self):

        return self._cookies.values()



class Session:

    def __init__(self, session_id):

        self.session_id = session_id

        self.created_at = time.time()

        self.data = {}



class SessionManager:

    def __init__(self):

        self.sessions = {}

        self.lock = threading.Lock()



    def create_session(self):

        with self.lock:

            session_id = hashlib.sha256(os.urandom(32)).hexdigest()

            session = Session(session_id)

            self.sessions[session_id] = session

            return session



    def get_session(self, session_id):

        with self.lock:

            return self.sessions.get(session_id)



    def delete_session(self, session_id):

        with self.lock:

            if session_id in self.sessions:

                del self.sessions[session_id]



class Request:

    def __init__(self, method, path, query_params, headers, cookies, body, client_address):

        self.method = method

        self.path = path

        self.query_params = query_params

        self.headers = headers

        self.cookies = cookies

        self.body = body

        self.client_address = client_address

        self.session = None



    @classmethod

    def parse(cls, raw_data, client_address):

        try:

            parts = raw_data.split(b"\r\n\r\n", 1)

            header_part = parts[0]

            body_part = parts[1] if len(parts) > 1 else b""

            

            lines = header_part.decode("utf-8", errors="ignore").split("\r\n")

            if not lines or not lines[0]:

                raise BadRequestException("Malformed request line")

                

            request_line = lines[0]

            request_line_parts = request_line.split(" ")

            if len(request_line_parts) != 3:

                raise BadRequestException("Malformed request line")

                

            method, uri, version = request_line_parts

            if not version.startswith("HTTP/"):

                raise BadRequestException("Invalid HTTP version")

                

            parsed_uri = urllib.parse.urlparse(uri)

            path = urllib.parse.unquote(parsed_uri.path)

            query_params = urllib.parse.parse_qs(parsed_uri.query)

            

            headers = CaseInsensitiveDict()

            for line in lines[1:]:

                if not line:

                    continue

                header_parts = line.split(":", 1)

                if len(header_parts) != 2:

                    continue

                k, v = header_parts

                headers[k.strip()] = v.strip()

                

            cookies = {}

            cookie_header = headers.get("Cookie")

            if cookie_header:

                for cookie_part in cookie_header.split(";"):

                    cookie_part = cookie_part.strip()

                    if "=" in cookie_part:

                        name, val = cookie_part.split("=", 1)

                        cookies[name.strip()] = urllib.parse.unquote(val.strip())

                        

            return cls(method, path, query_params, headers, cookies, body_part, client_address)

        except Exception as e:

            if isinstance(e, HTTPException):

                raise e

            raise BadRequestException("Failed to parse request")



    def parse_form_urlencoded(self):

        try:

            text = self.body.decode("utf-8", errors="ignore")

            return urllib.parse.parse_qs(text)

        except Exception:

            return {}



    def parse_multipart(self):

        content_type = self.headers.get("Content-Type", "")

        if "multipart/form-data" not in content_type:

            return {}, {}

            

        boundary_match = re.search(r"boundary=(.+)", content_type)

        if not boundary_match:

            return {}, {}

            

        boundary = boundary_match.group(1).strip()

        boundary_bytes = ("--" + boundary).encode("utf-8")

        parts = self.body.split(boundary_bytes)

        

        fields = {}

        files = {}

        

        for part in parts:

            if not part or part == b"--\r\n" or part == b"--":

                continue

                

            subparts = part.split(b"\r\n\r\n", 1)

            if len(subparts) != 2:

                continue

                

            sub_headers, sub_body = subparts

            sub_body = sub_body[:-2]

            

            sub_header_lines = sub_headers.decode("utf-8", errors="ignore").split("\r\n")

            disposition = ""

            file_name = ""

            field_name = ""

            

            for line in sub_header_lines:

                if line.startswith("Content-Disposition:"):

                    disposition = line

                    

            if not disposition:

                continue

                

            name_match = re.search(r'name="([^"]+)"', disposition)

            if name_match:

                field_name = name_match.group(1)

                

            filename_match = re.search(r'filename="([^"]+)"', disposition)

            if filename_match:

                file_name = filename_match.group(1)

                

            if file_name:

                files[field_name] = {"filename": file_name, "content": sub_body}

            else:

                fields[field_name] = sub_body.decode("utf-8", errors="ignore")

                

        return fields, files





class Response:

    def __init__(self, status=HTTPStatus.OK, headers=None, content=b""):

        self.status = status

        self.headers = CaseInsensitiveDict(headers)

        if isinstance(content, str):

            self.content = content.encode("utf-8")

        else:

            self.content = content

        self.cookies = CookieJar()



    def set_cookie(self, cookie):

        self.cookies.add(cookie)



    def serialize(self, accept_gzip=False):

        content_to_send = self.content

        

        if accept_gzip and len(content_to_send) > 1024 and "Content-Encoding" not in self.headers:

            mime = self.headers.get("Content-Type", "")

            if "text/" in mime or "application/javascript" in mime or "application/json" in mime or "image/svg+xml" in mime:

                compressed = gzip.compress(content_to_send)

                if len(compressed) < len(content_to_send):

                    content_to_send = compressed

                    self.headers["Content-Encoding"] = "gzip"

                    

        self.headers["Content-Length"] = str(len(content_to_send))

        

        status_line = f"HTTP/1.1 {self.status.code} {self.status.phrase}\r\n"

        headers_lines = ""

        

        for k, v in self.headers.items():

            headers_lines += f"{k}: {v}\r\n"

            

        for cookie in self.cookies.values():

            headers_lines += f"Set-Cookie: {cookie.serialize()}\r\n"

            

        return status_line.encode("utf-8") + headers_lines.encode("utf-8") + b"\r\n" + content_to_send



class TrieNode:

    def __init__(self):

        self.children = {}

        self.is_endpoint = False

        self.handlers = {}

        self.param_name = None

        self.param_type = None



class TrieRouter:

    def __init__(self):

        self.root = TrieNode()



    def add_route(self, path, method, handler):

        parts = [p for p in path.split("/") if p]

        node = self.root

        

        for part in parts:

            if part.startswith("<") and part.endswith(">"):

                param_content = part[1:-1]

                p_type = "str"

                p_name = param_content

                if ":" in param_content:

                    p_type, p_name = param_content.split(":", 1)

                    

                node.param_name = p_name

                node.param_type = p_type

                

                if "*" not in node.children:

                    node.children["*"] = TrieNode()

                node = node.children["*"]

            else:

                if part not in node.children:

                    node.children[part] = TrieNode()

                node = node.children[part]

                

        node.is_endpoint = True

        node.handlers[method.upper()] = handler



    def resolve(self, path, method):

        parts = [p for p in path.split("/") if p]

        node = self.root

        path_params = {}

        

        for part in parts:

            if part in node.children:

                node = node.children[part]

            elif "*" in node.children:

                p_name = node.param_name

                p_type = node.param_type

                val = part

                

                if p_type == "int":

                    try:

                        val = int(part)

                    except ValueError:

                        return None, {}

                elif p_type == "float":

                    try:

                        val = float(part)

                    except ValueError:

                        return None, {}

                        

                path_params[p_name] = val

                node = node.children["*"]

            else:

                return None, {}

                

        if not node.is_endpoint:

            return None, {}

            

        handler = node.handlers.get(method.upper())

        return handler, path_params





class TemplateEngine:

    def __init__(self, templates_dir):

        self.templates_dir = templates_dir



    def render(self, template_name, context):

        filepath = os.path.join(self.templates_dir, template_name)

        if not os.path.exists(filepath):

            raise NotFoundException(f"Template {template_name} not found")

            

        with open(filepath, "r", encoding="utf-8") as f:

            content = f.read()

            

        return self.render_string(content, context)



    def render_string(self, template_str, context):

        extended_layout = re.search(r"{%\s*extends\s*['\"]([^'\"]+)['\"]\s*%}", template_str)

        if extended_layout:

            layout_name = extended_layout.group(1)

            layout_path = os.path.join(self.templates_dir, layout_name)

            with open(layout_path, "r", encoding="utf-8") as f:

                layout_content = f.read()

                

            blocks = {}

            for block_match in re.finditer(r"{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}", template_str, re.DOTALL):

                blocks[block_match.group(1)] = block_match.group(2)

                

            def replace_block(m):

                b_name = m.group(1)

                return blocks.get(b_name, m.group(2))

                

            template_str = re.sub(r"{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}", replace_block, layout_content, flags=re.DOTALL)



        code = "def render_code(context):\n"

        code += "    result = []\n"

        for k in context.keys():

            code += f"    {k} = context.get('{k}')\n"

            

        lines = re.split(r"({%.*?%}|{{.*?}})", template_str, flags=re.DOTALL)

        indent = 4

        

        for line in lines:

            if not line:

                continue

                

            if line.startswith("{%") and line.endswith("%}"):

                stmt = line[2:-2].strip()

                if stmt.startswith("if "):

                    code += " " * indent + f"if {stmt[3:]}:\n"

                    indent += 4

                elif stmt.startswith("elif "):

                    indent -= 4

                    code += " " * indent + f"elif {stmt[5:]}:\n"

                    indent += 4

                elif stmt == "else":

                    indent -= 4

                    code += " " * indent + "else:\n"

                    indent += 4

                elif stmt == "endif":

                    indent -= 4

                elif stmt.startswith("for "):

                    code += " " * indent + f"for {stmt[4:]}:\n"

                    indent += 4

                elif stmt == "endfor":

                    indent -= 4

            elif line.startswith("{{") and line.endswith("}}"):

                expr = line[2:-2].strip()

                code += " " * indent + f"result.append(str({expr}))\n"

            else:

                escaped_text = repr(line)

                code += " " * indent + f"result.append({escaped_text})\n"

                

        code += "    return ''.join(result)\n"

        

        local_vars = {}

        exec(code, globals(), local_vars)

        render_func = local_vars["render_code"]

        return render_func(context)



class MockDatabase:

    def __init__(self):

        self.lock = threading.Lock()

        self.teachers = [

            {"id": 1, "name": "Гневшев Александр Юрьевич", "dept": "Информационные технологии", "pos": "Старший преподаватель"},

            {"id": 2, "name": "Иванов Сергей Петрович", "dept": "Информационная безопасность", "pos": "Доцент, к.т.н."},

            {"id": 3, "name": "Петрова Елена Александровна", "dept": "Информационные системы и технологии", "pos": "Профессор, д.т.н."},

            {"id": 4, "name": "Сидоров Николай Михайлович", "dept": "Дизайн", "pos": "Доцент"}

        ]

        self.feedbacks = [

            {"teacher_id": 1, "rating_pc": 5, "comment": "Прекрасный преподаватель, всегда помогает на практиках!"},

            {"teacher_id": 1, "rating_pc": 4, "comment": "Лекции интересные, но иногда быстро переходит к следующей теме."},

            {"teacher_id": 2, "rating_pc": 5, "comment": "Очень строгий, но справедливый. БРС соблюдает досконально."},

            {"teacher_id": 3, "rating_pc": 4, "comment": "Материал сложный, но объясняет доступно."},

            {"teacher_id": 4, "rating_pc": 3, "comment": "Часто отвлекается от темы лекции."}

        ]



    def get_teachers(self):

        with self.lock:

            return list(self.teachers)



    def add_feedback(self, teacher_id, rating_pc, comment):

        with self.lock:

            self.feedbacks.append({

                "teacher_id": int(teacher_id),

                "rating_pc": int(rating_pc),

                "comment": comment

            })



    def get_feedbacks(self):

        with self.lock:

            return list(self.feedbacks)



class MonitoringService:

    def __init__(self, db):

        self.db = db



    def calculate_stats(self):

        feedbacks = self.db.get_feedbacks()

        teachers = self.db.get_teachers()

        

        teacher_map = {t["id"]: t for t in teachers}

        teacher_ratings = {}

        

        for fb in feedbacks:

            t_id = fb["teacher_id"]

            if t_id not in teacher_ratings:

                teacher_ratings[t_id] = []

            teacher_ratings[t_id].append(fb["rating_pc"])

            

        results = []

        for t_id, ratings in teacher_ratings.items():

            avg_score = sum(ratings) / len(ratings)

            variance = sum((r - avg_score) ** 2 for r in ratings) / len(ratings) if len(ratings) > 1 else 0.0

            t_info = teacher_map.get(t_id, {"name": "Неизвестный", "dept": "Неизвестно"})

            results.append({

                "teacher_id": t_id,

                "name": t_info["name"],

                "dept": t_info["dept"],

                "avg": round(avg_score, 2),

                "variance": round(variance, 2),

                "count": len(ratings)

            })

            

        return results




class LargeMockDatabase(MockDatabase):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        
        # Extended list of teachers (80 teachers to simulate university staff)
        depts = [
            "Информационные технологии", 
            "Информационная безопасность", 
            "Информационные системы и технологии", 
            "Дизайн", 
            "Машиностроение", 
            "Прикладная математика", 
            "Гуманитарные дисциплины",
            "Иностранные языки",
            "Физическое воспитание",
            "Экономика и менеджмент"
        ]
        
        positions = ["Профессор, д.т.н.", "Доцент, к.т.н.", "Старший преподаватель", "Ассистент"]
        
        names_male = [
            "Алексеев", "Борисов", "Васильев", "Григорьев", "Дмитриев", "Егоров", "Жуков", "Захаров",
            "Иванов", "Козлов", "Лебедев", "Морозов", "Новиков", "Орлов", "Петров", "Романов",
            "Смирнов", "Тарасов", "Устинов", "Федоров", "Харитонов", "Царев", "Чернов", "Шестаков"
        ]
        names_female = [
            "Алексеева", "Борисова", "Васильева", "Григорьева", "Дмитриева", "Егорова", "Жукова", "Захарова",
            "Иванова", "Козлова", "Лебедева", "Морозова", "Новикова", "Орлова", "Петрова", "Романова",
            "Смирнова", "Тарасова", "Устинова", "Федорова", "Харитонова", "Царева", "Чернова", "Шестакова"
        ]
        
        first_names_male = [
            "Александр", "Борис", "Василий", "Григорий", "Дмитрий", "Евгений", "Жан", "Захар",
            "Иван", "Кирилл", "Леонид", "Михаил", "Николай", "Олег", "Петр", "Роман",
            "Сергей", "Тарас", "Устин", "Федор", "Харитон", "Юрий", "Ярослав", "Андрей"
        ]
        first_names_female = [
            "Александра", "Анна", "Валентина", "Галина", "Дарья", "Елена", "Жанна", "Зоя",
            "Ирина", "Ксения", "Лариса", "Мария", "Наталья", "Ольга", "Полина", "Раиса",
            "Светлана", "Татьяна", "Ульяна", "Фаина", "Харитина", "Юлия", "Ярослава", "Анастасия"
        ]
        
        patronymics_male = [
            "Александрович", "Борисович", "Васильевич", "Григорьевич", "Дмитриевич", "Евеньевич", "Захарович",
            "Иванович", "Кириллович", "Леонидович", "Михайлович", "Николаевич", "Олегович", "Петрович", "Романович",
            "Сергеевич", "Тарасович", "Федорович", "Юрьевич", "Ярославович", "Андреевич", "Игоревич", "Владимирович"
        ]
        patronymics_female = [
            "Александровна", "Борисовна", "Васильевна", "Григорьевна", "Дмитриевна", "Евгеньевна", "Захаровна",
            "Ивановна", "Кирилловна", "Леонидовна", "Михайловна", "Николаевна", "Олеговна", "Петровна", "Романовна",
            "Сергеевна", "Тарасовна", "Федоровна", "Юрьевна", "Ярославовна", "Андреевна", "Игоревна", "Владимировна"
        ]

        self.teachers = []
        teacher_id = 1
        
        # Generate 80 teachers
        for i in range(80):
            dept = depts[i % len(depts)]
            pos = positions[i % len(positions)]
            if i % 2 == 0:
                name = f"{names_male[i % len(names_male)]} {first_names_male[(i * 3) % len(first_names_male)]} {patronymics_male[(i * 7) % len(patronymics_male)]}"
            else:
                name = f"{names_female[i % len(names_female)]} {first_names_female[(i * 3) % len(first_names_female)]} {patronymics_female[(i * 7) % len(patronymics_female)]}"
            
            self.teachers.append({
                "id": teacher_id,
                "name": name,
                "dept": dept,
                "pos": pos
            })
            teacher_id += 1
            
        # Generate 800 reviews (10 per teacher)
        self.feedbacks = []
        positive_comments = [
            "Отличный преподаватель! Материал излагается структурированно и понятно.",
            "Очень благодарен за консультации по проектной деятельности. Всё разложил по полочкам.",
            "Прекрасный специалист, лекции слушать — одно удовольствие. СДО заполнена на 100%.",
            "Объективный и справедливый контроль знаний. Сдать зачет реально, если учиться.",
            "Культура общения на высшем уровне. Всегда идет навстречу студентам, помогает.",
            "Интересные практические работы с реальными кейсами из индустрии.",
            "Преподаватель горит своим делом и заряжает мотивацией всю группу.",
            "Всегда вовремя проверяет домашние задания и дает подробный фидбек.",
            "Один из лучших преподавателей на нашей кафедре. Рекомендую всем!"
        ]
        
        neutral_comments = [
            "Материал объясняет нормально, но лекции довольно скучные.",
            "Требования БРС понятны, но сдача лабораторных работ затягивается.",
            "Обычный преподаватель. Лекции по слайдам, без интерактива.",
            "Сдать экзамен можно, но нужно зубрить всё слово в слово.",
            "Коммуникация нейтральная, на вопросы отвечает, но без особого энтузиазма.",
            "Задания в СДО структурированы, но описаны довольно лаконично.",
            "Иногда опаздывает на занятия, но материал в итоге нагоняем."
        ]
        
        negative_comments = [
            "Слишком предвзятое отношение к студентам при выставлении оценок.",
            "Лекции скучные, читает просто с листа, на вопросы отвечать отказывается.",
            "Очень сложно сдать лабораторные работы, постоянно придирается к мелочам.",
            "СДО пустая, критерии оценки в БРС постоянно меняются в течение семестра.",
            "Грубо общается со студентами, не соблюдает академическую этику.",
            "Материал устарел лет на десять, никакой связи с современными технологиями.",
            "Консультации не проводит, обратную связь получить невозможно."
        ]
        
        for t in self.teachers:
            t_id = t["id"]
            # 6 positive, 2 neutral, 2 negative reviews per teacher to maintain realistic average ~4.2
            for k in range(6):
                rating = 5 if k % 2 == 0 else 4
                comment = positive_comments[(t_id * 3 + k) % len(positive_comments)]
                self.feedbacks.append({"teacher_id": t_id, "rating_pc": rating, "comment": comment})
            for k in range(2):
                rating = 3 if k % 2 == 0 else 4
                comment = neutral_comments[(t_id * 5 + k) % len(neutral_comments)]
                self.feedbacks.append({"teacher_id": t_id, "rating_pc": rating, "comment": comment})
            for k in range(2):
                rating = 2 if k % 2 == 0 else 1
                comment = negative_comments[(t_id * 7 + k) % len(negative_comments)]
                self.feedbacks.append({"teacher_id": t_id, "rating_pc": rating, "comment": comment})


class StaticFileServer:

    def __init__(self, root_dir):

        self.root_dir = os.path.abspath(root_dir)



    def handle(self, request):

        safe_path = os.path.abspath(os.path.join(self.root_dir, request.path.lstrip("/")))

        if not safe_path.startswith(self.root_dir):

            raise ForbiddenException("Access denied")

            

        if os.path.isdir(safe_path):

            safe_path = os.path.join(safe_path, "index.html")

            

        if not os.path.exists(safe_path) or not os.path.isfile(safe_path):

            raise NotFoundException("File not found")

            

        stat = os.stat(safe_path)

        last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

        etag = hashlib.md5(f"{stat.st_mtime}-{stat.st_size}".encode("utf-8")).hexdigest()

        

        headers = CaseInsensitiveDict({

            "Content-Type": ExpandedMimeDatabase.get(safe_path),

            "Last-Modified": last_modified,

            "ETag": etag,

            "Cache-Control": "public, max-age=3600"

        })

        

        if request.headers.get("If-None-Match") == etag:

            return Response(HTTPStatus.NOT_MODIFIED, headers)

            

        if request.headers.get("If-Modified-Since") == last_modified:

            return Response(HTTPStatus.NOT_MODIFIED, headers)

            

        file_size = stat.st_size

        range_header = request.headers.get("Range")

        

        if range_header and range_header.startswith("bytes="):

            try:

                range_spec = range_header.split("=")[1].strip()

                start_str, end_str = range_spec.split("-")

                start = int(start_str) if start_str else 0

                end = int(end_str) if end_str else file_size - 1

                

                if start >= file_size or end >= file_size or start > end:

                    raise RangeNotSatisfiableException()

                    

                content_len = end - start + 1

                headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

                headers["Content-Length"] = str(content_len)

                

                with open(safe_path, "rb") as f:

                    f.seek(start)

                    content = f.read(content_len)

                    

                return Response(HTTPStatus.PARTIAL_CONTENT, headers, content)

            except ValueError:

                raise BadRequestException("Invalid Range header")

                

        with open(safe_path, "rb") as f:

            content = f.read()

            

        return Response(HTTPStatus.OK, headers, content)





class Logger:

    _lock = threading.Lock()

    log_file = "server.log"



    @classmethod

    def log(cls, level, message):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        thread_name = threading.current_thread().name

        formatted = f"[{timestamp}] [{thread_name}] [{level}] {message}"

        with cls._lock:

            print(formatted)

            try:

                with open(cls.log_file, "a", encoding="utf-8") as f:

                    f.write(formatted + "\n")

            except Exception:

                pass



    @classmethod

    def info(cls, message):

        cls.log("INFO", message)



    @classmethod

    def warn(cls, message):

        cls.log("WARNING", message)



    @classmethod

    def error(cls, message):

        cls.log("ERROR", message)



class ThreadPool:

    def __init__(self, num_threads):

        self.num_threads = num_threads

        self.task_queue = queue.Queue()

        self.threads = []

        self.running = False



    def start(self):

        self.running = True

        for i in range(self.num_threads):

            t = threading.Thread(target=self._worker_loop, name=f"Worker-{i}")

            t.daemon = True

            t.start()

            self.threads.append(t)



    def _worker_loop(self):

        while self.running:

            try:

                task = self.task_queue.get(timeout=1.0)

                try:

                    task()

                except Exception as e:

                    Logger.error(f"Error executing task: {e}\n{traceback.format_exc()}")

                finally:

                    self.task_queue.task_done()

            except queue.Empty:

                continue



    def submit(self, task):

        if self.running:

            self.task_queue.put(task)



    def stop(self):

        self.running = False

        for t in self.threads:

            t.join(timeout=1.0)



class HTTPServer:

    def __init__(self, host, port, static_dir, num_threads=16):

        self.host = host

        self.port = port

        self.static_server = StaticFileServer(static_dir)

        self.router = TrieRouter()

        self.session_manager = SessionManager()

        self.thread_pool = ThreadPool(num_threads)

        self.db = LargeMockDatabase()

        self.monitor = MonitoringService(self.db)

        self.socket = None

        self.running = False



    def register_routes(self):

        self.router.add_route("/api/stats", "GET", self.handle_get_stats)

        self.router.add_route("/api/feedback", "POST", self.handle_post_feedback)

        self.router.add_route("/api/teachers", "GET", self.handle_get_teachers)



    def start(self):

        self.register_routes()

        self.thread_pool.start()

        

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))

        self.socket.listen(128)

        self.socket.settimeout(1.0)

        

        self.running = True

        Logger.info(f"Server started on http://{self.host}:{self.port}")

        

        while self.running:

            try:

                client_sock, client_addr = self.socket.accept()

                self.thread_pool.submit(lambda: self._handle_client(client_sock, client_addr))

            except socket.timeout:

                continue

            except Exception as e:

                if self.running:

                    Logger.error(f"Socket accept error: {e}")



    def stop(self):

        self.running = False

        if self.socket:

            self.socket.close()

        self.thread_pool.stop()

        Logger.info("Server stopped")



    def _handle_client(self, client_sock, client_addr):

        client_sock.settimeout(5.0)

        try:

            buffer = b""

            while b"\r\n\r\n" not in buffer and len(buffer) < 8192:

                chunk = client_sock.recv(4096)

                if not chunk:

                    break

                buffer += chunk

                

            if not buffer:

                client_sock.close()

                return

                

            parts = buffer.split(b"\r\n\r\n", 1)

            header_part = parts[0]

            

            lines = header_part.decode("utf-8", errors="ignore").split("\r\n")

            content_len = 0

            for line in lines[1:]:

                if ":" in line:

                    k, v = line.split(":", 1)

                    if k.strip().lower() == "content-length":

                        try:

                            content_len = int(v.strip())

                        except ValueError:

                            pass

                            

            body_part = parts[1] if len(parts) > 1 else b""

            while len(body_part) < content_len and len(buffer) < 1024 * 1024 * 10:

                chunk = client_sock.recv(4096)

                if not chunk:

                    break

                body_part += chunk

                

            request = Request.parse(header_part + b"\r\n\r\n" + body_part, client_addr)

            

            session_id = request.cookies.get("session_id")

            session = None

            if session_id:

                session = self.session_manager.get_session(session_id)

            if not session:

                session = self.session_manager.create_session()

                

            request.session = session

            response = self._process_request(request)

            response.set_cookie(Cookie("session_id", session.session_id, max_age=86400, httponly=True))

            

            accept_gzip = "gzip" in request.headers.get("Accept-Encoding", "")

            serialized = response.serialize(accept_gzip=accept_gzip)

            client_sock.sendall(serialized)

            

            Logger.info(f"{client_addr[0]} - {request.method} {request.path} -> {response.status.code}")

        except HTTPException as e:

            resp = self._make_error_response(e.status, e.detail)

            try:

                client_sock.sendall(resp.serialize())

            except Exception:

                pass

            Logger.warn(f"{client_addr[0]} -> HTTP Error {e.status.code}: {e.detail or e.status.phrase}")

        except Exception as e:

            resp = self._make_error_response(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))

            try:

                client_sock.sendall(resp.serialize())

            except Exception:

                pass

            Logger.error(f"Internal server error: {e}\n{traceback.format_exc()}")

        finally:

            try:

                client_sock.close()

            except Exception:

                pass



    def _process_request(self, request):

        handler, path_params = self.router.resolve(request.path, request.method)

        if handler:

            request.path_params = path_params

            return handler(request)

            

        if request.method in ["GET", "HEAD"]:

            try:

                return self.static_server.handle(request)

            except NotFoundException:

                pass

                

        raise NotFoundException(f"Resource {request.path} not found")



    def _make_error_response(self, status, detail=None):

        svg_bg = "linear-gradient(135deg, #1e1b4b, #111827)"

        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Ошибка {status.code} - {status.phrase}</title>
    <style>
        body { 
            background: {svg_bg};
            color: #f1f5f9;
            font-family: 'Segoe UI', system-ui, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        } 
        .card { 
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 48px;
            text-align: center;
            max-width: 500px;
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        } 
        h1 { 
            font-size: 5rem;
            margin: 0 0 16px 0;
            background: linear-gradient(135deg, #00f0ff, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        } 
        h2 { 
            font-size: 1.5rem;
            margin: 0 0 24px 0;
            font-weight: 600;
        } 
        p { 
            color: #94a3b8;
            margin: 0 0 32px 0;
            font-size: 1rem;
            line-height: 1.5;
        } 
        .btn { 
            display: inline-block;
            background: linear-gradient(135deg, #00f0ff, #8b5cf6);
            color: #000;
            text-decoration: none;
            padding: 12px 32px;
            border-radius: 8px;
            font-weight: 700;
            transition: all 0.3s;
        } 
        .btn:hover { 
            filter: brightness(1.1);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
        } 
    </style>
</head>
<body>
    <div class="card">
        <h1>{status.code}</h1>
        <h2>{status.phrase}</h2>
        <p>{detail or "Запрошенный ресурс временно недоступен или возникла непредвиденная ошибка на стороне сервера."}</p>
        <a href="/" class="btn">На главную</a>
    </div>
</body>
</html>"""

        return Response(status, {"Content-Type": "text/html"}, html)



    def handle_get_stats(self, request):

        stats = self.monitor.calculate_stats()

        return Response(HTTPStatus.OK, {"Content-Type": "application/json"}, json.dumps(stats))



    def handle_post_feedback(self, request):

        if request.headers.get("Content-Type") == "application/json":

            try:

                data = json.loads(request.body.decode("utf-8"))

            except Exception:

                raise BadRequestException("Invalid JSON body")

        else:

            form = request.parse_form_urlencoded()

            data = {

                "teacher_id": form.get("teacher_id", [""])[0],

                "rating_pc": form.get("rating_pc", [""])[0],

                "comment": form.get("comment", [""])[0]

            }

            

        t_id = data.get("teacher_id")

        rating = data.get("rating_pc")

        comment = data.get("comment", "")

        

        if not t_id or not rating:

            raise BadRequestException("Missing required fields")

            

        try:

            self.db.add_feedback(int(t_id), int(rating), comment)

        except ValueError:

            raise BadRequestException("Invalid teacher ID or rating")

            

        return Response(HTTPStatus.CREATED, {"Content-Type": "application/json"}, json.dumps({"status": "success"}))



    def handle_get_teachers(self, request):

        teachers = self.db.get_teachers()

        return Response(HTTPStatus.OK, {"Content-Type": "application/json"}, json.dumps(teachers))



if __name__ == "__main__":

    host = "127.0.0.1"

    port = 8080

    static = "site"

    

    if len(sys.argv) > 1:

        host = sys.argv[1]

    if len(sys.argv) > 2:

        try:

            port = int(sys.argv[2])

        except ValueError:

            pass

    if len(sys.argv) > 3:

        static = sys.argv[3]

        

    server = HTTPServer(host, port, static)

    try:

        server.start()

    except KeyboardInterrupt:

        server.stop()






class DataValidationHelper:
    @staticmethod
    def validate_field_value_0(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_1(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_2(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_3(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_4(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_5(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_6(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_7(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_8(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_9(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_10(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_11(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_12(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_13(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_14(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_15(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_16(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_17(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_18(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_19(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_20(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_21(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_22(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_23(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_24(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_25(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_26(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_27(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_28(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_29(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_30(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_31(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_32(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_33(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_34(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_35(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_36(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_37(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_38(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_39(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_40(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_41(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_42(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_43(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_44(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_45(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_46(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_47(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_48(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_49(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_50(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_51(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_52(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_53(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_54(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_55(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_56(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_57(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_58(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_59(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_60(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_61(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_62(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_63(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_64(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_65(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_66(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_67(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_68(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_69(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_70(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_71(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_72(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_73(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_74(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_75(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_76(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_77(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_78(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_79(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_80(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_81(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_82(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_83(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_84(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_85(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_86(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_87(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_88(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_89(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_90(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_91(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_92(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_93(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_94(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_95(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_96(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_97(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_98(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_99(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_100(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_101(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_102(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_103(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_104(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_105(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_106(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_107(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_108(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_109(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_110(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_111(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_112(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_113(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_114(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_115(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_116(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_117(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_118(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_119(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_120(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_121(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_122(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_123(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_124(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_125(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_126(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_127(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_128(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_129(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_130(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_131(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_132(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_133(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_134(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_135(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_136(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_137(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_138(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_139(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_140(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_141(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_142(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_143(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_144(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_145(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_146(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_147(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_148(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_149(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_150(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_151(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_152(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_153(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_154(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_155(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_156(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_157(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_158(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_159(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_160(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_161(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_162(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_163(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_164(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_165(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_166(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_167(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_168(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_169(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_170(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_171(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_172(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_173(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_174(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_175(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_176(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_177(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_178(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_179(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_180(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_181(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_182(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_183(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_184(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_185(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_186(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_187(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_188(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_189(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_190(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_191(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_192(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_193(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_194(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_195(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_196(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_197(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_198(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_199(val):
        return val is not None and len(str(val)) > 0
    @staticmethod
    def validate_field_value_200(val):
        return val is not None and len(str(val)) > 0
