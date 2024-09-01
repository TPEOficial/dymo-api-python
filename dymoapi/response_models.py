from pydantic import BaseModel
from typing import List

class UrlEncryptResponse(BaseModel):
    original: str
    code: str
    encrypt: str

class IsValidPwdDetails(BaseModel):
    validation: str
    message: str

class IsValidPwdResponse(BaseModel):
    valid: bool
    password: str
    details: List[IsValidPwdDetails]


class SatinizerFormats(BaseModel):
    ascii: bool
    bitcoinAddress: bool
    cLikeIdentifier: bool
    coordinates: bool
    crediCard: bool
    date: bool
    discordUsername: bool
    doi: bool
    domain: bool
    e164Phone: bool
    email: bool
    emoji: bool
    hanUnification: bool
    hashtag: bool
    hyphenWordBreak: bool
    ipv6: bool
    ip: bool
    jiraTicket: bool
    macAddress: bool
    name: bool
    number: bool
    panFromGstin: bool
    password: bool
    port: bool
    tel: bool
    text: bool
    semver: bool
    ssn: bool
    uuid: bool
    url: bool
    urlSlug: bool
    username: bool

class SatinizerIncludes(BaseModel):
    spaces: bool
    hasSql: bool
    hasNoSql: bool
    letters: bool
    uppercase: bool
    lowercase: bool
    symbols: bool
    digits: bool


class SatinizerResponse(BaseModel):
    input: str
    formats: SatinizerFormats
    includes: SatinizerIncludes