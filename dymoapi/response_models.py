from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Union, Optional, Literal, Any

class VerifyPlugins(Enum):
    COMPROMISE_DETECTOR = "compromiseDetector"
    NSFW = "nsfw"
    REPUTATION = "reputation"
    TOR_NETWORK = "torNetwork"
    TYPOSQUATTING = "typosquatting"
    URL_SHORTENER = "urlShortener"
    BLOCKLIST = "blocklist"

class PhoneData(BaseModel):
    iso: Optional[str] = None
    phone: str

class CreditCardData(BaseModel):
    pan: Union[str, int]
    expirationDate: Optional[str] = None
    cvc: Optional[Union[str, int]] = None
    cvv: Optional[Union[str, int]] = None

class Validator(BaseModel):
    email: Optional[str] = None
    phone: Optional[Union[PhoneData, str]] = None
    domain: Optional[str] = None
    creditCard: Optional[Union[str, CreditCardData]] = None
    ip: Optional[str] = None
    wallet: Optional[str] = None
    plugins: Optional[List[VerifyPlugins]] = None

class UrlEncryptResponse(BaseModel):
    original: str
    code: str
    encrypt: str

class IsValidPwdData(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    bannedWords: Optional[Union[str, List[str]]] = None
    min: Optional[int] = None
    max: Optional[int] = None

class IsValidPwdDetails(BaseModel):
    validation: str
    message: str

class IsValidPwdResponse(BaseModel):
    valid: bool
    password: str
    details: List[IsValidPwdDetails]

class InputSanitizerData(BaseModel):
    input: Optional[str] = None

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
    lat: Optional[float] = None
    lon: Optional[float] = None

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

class DataVerifierEmail(BaseModel):
    valid: Optional[bool] = None
    fraud: Optional[bool] = None
    proxiedEmail: Optional[bool] = None
    freeSubdomain: Optional[bool] = None
    corporate: Optional[bool] = None
    email: Optional[str] = None
    realUser: Optional[str] = None
    didYouMean: Optional[Union[str, bool]] = None
    noReply: Optional[bool] = None
    customTLD: Optional[bool] = None
    domain: Optional[str] = None
    roleAccount: Optional[bool] = None
    plugins: Optional[Dict[str, str]] = None

class CarrierInfo(BaseModel):
    carrierName: str
    accuracy: float
    carrierCountry: str
    carrierCountryCode: str

class DataVerifierPhone(BaseModel):
    valid: Optional[bool] = None
    fraud: Optional[bool] = None
    phone: Optional[str] = None 
    prefix: Optional[str] = None
    number: Optional[str] = None
    lineType: Literal[
        "PREMIUM_RATE", "TOLL_FREE", "SHARED_COST", "VOIP", "PERSONAL_NUMBER",
        "PAGER", "UAN", "VOICEMAIL", "FIXED_LINE_OR_MOBILE", "FIXED_LINE",
        "MOBILE", "Unknown"
    ]
    carrierInfo: Optional[CarrierInfo] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    plugins: Optional[Dict[str, str]] = None

class DataVerifierDomain(BaseModel):
    valid: Optional[bool] = None
    fraud: Optional[bool] = None
    freeSubdomain: Optional[bool] = None
    customTLD: Optional[bool] = None
    domain: Optional[str] = None
    plugins: Optional[Dict[str, str]] = None

class DataVerifierCreditCard(BaseModel):
    valid: Optional[bool] = None
    fraud: Optional[bool] = None
    test: Optional[bool] = None
    type: Optional[str] = None
    creditCard: Optional[str] = None
    plugins: Optional[Dict[str, str]] = None

class DataVerifierIp(BaseModel):
    valid: bool
    type: Optional[str] = None
    _class: Optional[str] = None
    fraud: Optional[bool] = None
    ip: Optional[str] = None
    continent: Optional[str] = None
    continentCode: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None
    regionName: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    zipCode: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = None
    offset: Optional[float | str] = None
    currency: Optional[str] = None
    isp: Optional[str] = None
    org: Optional[str] = None
    _as: Optional[str] = None
    asname: Optional[str] = None
    mobile: Optional[bool | str] = None
    proxy: Optional[bool | str] = None
    hosting: Optional[bool | str] = None
    plugins: Optional[Dict[str, str]] = None

class DataVerifierResponse(BaseModel):
    email: Optional[DataVerifierEmail]
    phone: Optional[DataVerifierPhone]
    domain: Optional[DataVerifierDomain]
    creditCard: Optional[DataVerifierCreditCard]
    ip: Optional[DataVerifierIp]

class SRNG(BaseModel):
    min: int
    max: int
    quantity: Optional[int] = None

class SRNGResponse(BaseModel):
    values: List[Dict[str, Union[int, float]]]
    executionTime: Union[int, float]

class SendEmailResponse(BaseModel):
    status: Union[bool, str]
    error: Optional[str] = None
    warning: Optional[str] = None

class EmailStatus(BaseModel):
    status: bool
    error: Optional[str] = None

class ExtractWithTextlyResponse(BaseModel):
    __root__: Any