from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, RootModel, Field
from typing import Any, Dict, List, Union, Optional, Literal

ReputationPlugin = Literal["low", "medium", "high", "very-high", "education", "governmental", "unknown"]
TyposquattingPlugin = Literal[0,1,2,3,4,5,6,7,8,9,10]

class MxRecord(BaseModel):
    priority: int
    exchange: str

class Plugins(BaseModel):
    blocklist: Optional[bool]
    gravatarUrl: Optional[str]
    compromiseDetector: Optional[bool]
    mxRecords: Optional[List[MxRecord]]
    nsfw: Optional[bool]
    reputation: Optional[ReputationPlugin]
    riskScore: Optional[float]
    torNetwork: Optional[bool]
    typosquatting: Optional[TyposquattingPlugin]
    urlShortener: Optional[bool]

class VerifyPlugins(Enum):
    BLOCKLIST = "blocklist"
    COMPROMISE_DETECTOR = "compromiseDetector"
    GRAVATAR_URL = "gravatarUrl"
    MX_RECORDS = "mxRecords"
    NSFW = "nsfw"
    REPUTATION = "reputation"
    RISK_SCORE = "riskScore"
    TOR_NETWORK = "torNetwork"
    TYPOSQUATTING = "typosquatting"
    URL_SHORTENER = "urlShortener"

class PhoneData(BaseModel):
    iso: Optional[str]
    phone: str

class CreditCardData(BaseModel):
    pan: Union[str, int]
    expirationDate: Optional[str]
    cvc: Optional[Union[str, int]]
    cvv: Optional[Union[str, int]]

class Validator(BaseModel):
    url: Optional[str]
    email: Optional[str]
    phone: Optional[Union[PhoneData, str]]
    domain: Optional[str]
    creditCard: Optional[Union[str, CreditCardData]]
    ip: Optional[str]
    wallet: Optional[str]
    userAgent: Optional[str]
    iban: Optional[str]
    plugins: Optional[List[VerifyPlugins]]

class UrlEncryptResponse(BaseModel):
    original: str
    code: str
    encrypt: str

class IsValidPwdData(BaseModel):
    email: Optional[str]
    password: Optional[str]
    bannedWords: Optional[Union[str, List[str]]]
    min: Optional[int]
    max: Optional[int]

class IsValidPwdDetails(BaseModel):
    validation: str
    message: str

class IsValidPwdResponse(BaseModel):
    valid: bool
    password: str
    details: List[IsValidPwdDetails]

class InputSanitizerData(BaseModel):
    input: Optional[str]

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

class PrayerTimesData(BaseModel):
    lat: Optional[float]
    lon: Optional[float]

class PrayerTimes(BaseModel):
    coordinates: str
    date: str
    calculationParameters: str
    fajr: str
    sunrise: str
    dhuhr: str
    asr: str
    sunset: str
    maghrib: str
    isha: str

class PrayerTimesByTimezone(BaseModel):
    timezone: str
    prayerTimes: PrayerTimes

class PrayerTimesResponse(BaseModel):
    country: str
    prayerTimesByTimezone: List[PrayerTimesByTimezone]

class DataVerifierURL(BaseModel):
    valid: Optional[bool]
    fraud: Optional[bool]
    freeSubdomain: Optional[bool]
    customTLD: Optional[bool]
    url: Optional[str]
    domain: Optional[str]
    plugins: Optional[Plugins]

class DataVerifierEmail(BaseModel):
    valid: Optional[bool]
    fraud: Optional[bool]
    proxiedEmail: Optional[bool]
    freeSubdomain: Optional[bool]
    corporate: Optional[bool]
    email: Optional[str]
    realUser: Optional[str]
    didYouMean: Optional[Union[str, bool]]
    noReply: Optional[bool]
    customTLD: Optional[bool]
    domain: Optional[str]
    roleAccount: Optional[bool]
    plugins: Optional[Plugins]

class CarrierInfo(BaseModel):
    carrierName: str
    accuracy: float
    carrierCountry: str
    carrierCountryCode: str

class DataVerifierPhone(BaseModel):
    valid: Optional[bool]
    fraud: Optional[bool]
    phone: Optional[str] 
    prefix: Optional[str]
    number: Optional[str]
    lineType: Literal[
        "PREMIUM_RATE", "TOLL_FREE", "SHARED_COST", "VOIP", "PERSONAL_NUMBER",
        "PAGER", "UAN", "VOICEMAIL", "FIXED_LINE_OR_MOBILE", "FIXED_LINE",
        "MOBILE", "Unknown"
    ]
    carrierInfo: Optional[CarrierInfo]
    country: Optional[str]
    countryCode: Optional[str]
    plugins: Optional[Plugins]

class DataVerifierDomain(BaseModel):
    valid: Optional[bool]
    fraud: Optional[bool]
    freeSubdomain: Optional[bool]
    customTLD: Optional[bool]
    domain: Optional[str]
    plugins: Optional[Plugins]

class DataVerifierCreditCard(BaseModel):
    valid: Optional[bool]
    fraud: Optional[bool]
    test: Optional[bool]
    type: Optional[str]
    creditCard: Optional[str]
    plugins: Optional[Plugins]

class DataVerifierIp(BaseModel):
    valid: bool
    type: Optional[str]
    _class: Optional[str]
    fraud: Optional[bool]
    ip: Optional[str]
    continent: Optional[str]
    continentCode: Optional[str]
    country: Optional[str]
    countryCode: Optional[str]
    region: Optional[str]
    regionName: Optional[str]
    city: Optional[str]
    district: Optional[str]
    zipCode: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    timezone: Optional[str]
    offset: Optional[float | str]
    currency: Optional[str]
    isp: Optional[str]
    org: Optional[str]
    _as: Optional[str]
    asname: Optional[str]
    mobile: Optional[bool | str]
    proxy: Optional[bool | str]
    hosting: Optional[bool | str]
    plugins: Optional[Plugins]

class DataVerifierDevice(BaseModel):
    type: Optional[str]
    brand: Optional[str]

class DataVerifierUserAgent(BaseModel):
    valid: bool
    type: Optional[str]
    clientSlug: Optional[str]
    clientName: Optional[str]
    version: Optional[str]
    userAgent: Optional[str]
    fraud: Optional[bool]
    bot: Optional[bool]
    info: Optional[str]
    os: Optional[str]
    device: DataVerifierDevice
    plugins: Optional[Dict[str, Any]]

class DataVerifierIBAN(BaseModel):
    valid: bool
    fraud: Optional[bool]
    iban: Optional[str]
    bban: Optional[str]
    bic: Optional[str] = "unknown"
    country: Optional[str]
    countryCode: Optional[str]
    accountNumber: Optional[str]
    branchIdentifier: Optional[str]
    bankIdentifier: Optional[str]
    plugins: Optional[Dict[str, Any]]

class DataVerifierResponse(BaseModel):
    url: Optional[DataVerifierURL]
    email: Optional[DataVerifierEmail]
    phone: Optional[DataVerifierPhone]
    domain: Optional[DataVerifierDomain]
    creditCard: Optional[DataVerifierCreditCard]
    ip: Optional[DataVerifierIp]
    userAgent: Optional[DataVerifierUserAgent]
    iban: Optional[DataVerifierIBAN]

class SRNG(BaseModel):
    min: int
    max: int
    quantity: Optional[int]

class SRNGResponse(BaseModel):
    values: List[Dict[str, Union[int, float]]]
    executionTime: Union[int, float]

class SendEmailResponse(BaseModel):
    status: Union[bool, str]
    error: Optional[str]
    warning: Optional[str]

class EmailStatus(BaseModel):
    status: bool
    error: Optional[str]

class JsonSchemaProperty(BaseModel):
    type: Literal["string", "number", "boolean", "array", "object"]
    items: Optional[JsonSchemaProperty]
    properties: Optional[Dict[str, JsonSchemaProperty]]
    required: Optional[List[str]]
    description: Optional[str]
    format: Optional[str]
    enum: Optional[List[Any]]
    minimum: Optional[float]
    maximum: Optional[float]
    minLength: Optional[int]
    maxLength: Optional[int]
    pattern: Optional[str]

class Textly(BaseModel):
    data: str = Field(..., description="Input text")
    format: Dict[str, JsonSchemaProperty] = Field(..., description="Output schema")

class TextlyResponse(RootModel):
    root: Any