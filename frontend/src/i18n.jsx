import { createContext, useContext, useState, useEffect } from 'react';

/* ── Supported languages ─────────────────────────────────────────────── */
export const LANGUAGES = [
  { code: 'en', label: 'English',  flag: '🇬🇧', short: 'EN' },
  { code: 'hi', label: 'हिन्दी',    flag: '🇮🇳', short: 'HI' },
  { code: 'mr', label: 'मराठी',    flag: '🇮🇳', short: 'MR' },
  { code: 'ta', label: 'தமிழ்',    flag: '🇮🇳', short: 'TA' },
  { code: 'te', label: 'తెలుగు',   flag: '🇮🇳', short: 'TE' },
];

/* ── Translation dictionary ──────────────────────────────────────────── */
export const T = {
  // Navbar
  home:         { en: 'Home',         hi: 'होम',         mr: 'मुख्य',       ta: 'முகப்பு',     te: 'హోమ్' },
  cropAdvisor:  { en: 'Crop Advisor',  hi: 'फसल सलाहकार', mr: 'पीक सल्लागार', ta: 'பயிர் ஆலோசகர்', te: 'పంట సలహాదారు' },
  plantDoctor:  { en: 'Plant Doctor',  hi: 'पौध चिकित्सक', mr: 'वनस्पती डॉक्टर', ta: 'தாவர மருத்துவர்', te: 'మొక్కల వైద్యుడు' },
  economics:    { en: 'Economics',     hi: 'अर्थशास्त्र',  mr: 'अर्थशास्त्र',  ta: 'பொருளாதாரம்',   te: 'ఆర్థిక శాస్త్రం' },
  agroBot:      { en: 'AgroBot',       hi: 'एग्रोबॉट',    mr: 'अग्रोबॉट',    ta: 'அக்ரோபாட்',    te: 'అగ్రోబాట్' },
  signIn:       { en: 'Sign In',       hi: 'लॉग इन',      mr: 'साइन इन',     ta: 'உள்நுழை',     te: 'సైన్ ఇన్' },
  signOut:      { en: 'Sign out',      hi: 'लॉग आउट',     mr: 'साइन आउट',    ta: 'வெளியேறு',    te: 'సైన్ అవుట్' },

  // Auth page
  signInLabel:  { en: 'Sign In',       hi: 'लॉग इन',       mr: 'साइन इन',     ta: 'உள்நுழை',     te: 'సైన్ ఇన్' },
  signUpLabel:  { en: 'Sign Up',       hi: 'साइन अप',      mr: 'नोंदणी करा',  ta: 'பதிவு செய்',  te: 'సైన్ అప్' },
  emailAddr:    { en: 'Email Address', hi: 'ईमेल पता',     mr: 'ईमेल पत्ता',  ta: 'மின்னஞ்சல்',  te: 'ఈమెయిల్' },
  password:     { en: 'Password',      hi: 'पासवर्ड',      mr: 'पासवर्ड',     ta: 'கடவுச்சொல்',  te: 'పాస్వర్డ్' },
  confirmPass:  { en: 'Confirm Password', hi: 'पासवर्ड दोबारा', mr: 'पासवर्ड पुन्हा', ta: 'கடவுச்சொல் உறுதி', te: 'పాస్వర్డ్ నిర్ధారించు' },
  fullName:     { en: 'Full Name',     hi: 'पूरा नाम',     mr: 'पूर्ण नाव',   ta: 'முழு பெயர்',  te: 'పూర్తి పేరు' },
  signingIn:    { en: 'Signing in…',   hi: 'लॉग इन हो रहा…', mr: 'साइन इन होत आहे…', ta: 'உள்நுழைகிறது…', te: 'సైన్ ఇన్ అవుతోంది…' },
  creating:     { en: 'Creating account…', hi: 'खाता बना रहा…', mr: 'खाते तयार होत आहे…', ta: 'கணக்கு உருவாக்குகிறது…', te: 'ఖాతా సృష్టిస్తోంది…' },
  createAcct:   { en: 'Create Account', hi: 'खाता बनाएं', mr: 'खाते तयार करा', ta: 'கணக்கு உருவாக்கு', te: 'ఖాతా సృష్టించు' },
  dashboardSub: { en: 'Sign in to your farming dashboard', hi: 'अपने कृषि डैशबोर्ड में साइन इन करें', mr: 'तुमच्या शेती डॅशबोर्डमध्ये साइन इन करा', ta: 'உங்கள் விவசாய டாஷ்போர்டில் உள்நுழையுங்கள்', te: 'మీ వ్యవసాయ డాష్‌బోర్డ్‌లో సైన్ ఇన్ చేయండి' },
  growSub:      { en: 'Start growing smarter today', hi: 'आज से चतुराई से उगाना शुरू करें', mr: 'आजपासून हुशारीने शेती सुरू करा', ta: 'இன்றே புத்திசாலித்தனமாக வளரத் தொடங்குங்கள்', te: 'ఈరోజు తెలివిగా పెరగడం ప్రారంభించండి' },

  // Misc
  fillAll:      { en: 'Please fill all fields', hi: 'कृपया सभी फ़ील्ड भरें', mr: 'कृपया सर्व फील्ड भरा', ta: 'அனைத்து புலங்களையும் நிரப்பவும்', te: 'అన్ని ఫీల్డ్‌లు నింపండి' },
  passNoMatch:  { en: 'Passwords do not match', hi: 'पासवर्ड मेल नहीं खाते', mr: 'पासवर्ड जुळत नाहीत', ta: 'கடவுச்சொற்கள் பொருந்தவில்லை', te: 'పాస్వర్డ్‌లు సరిపోలలేదు' },
  passShort:    { en: 'Password must be at least 6 characters', hi: 'पासवर्ड कम से कम 6 अक्षर का होना चाहिए', mr: 'पासवर्ड किमान 6 अक्षरांचा असणे आवश्यक आहे', ta: 'கடவுச்சொல் குறைந்தது 6 எழுத்துகள் இருக்க வேண்டும்', te: 'పాస్వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి' },
  welcome:      { en: 'Welcome back! Redirecting…', hi: 'वापस स्वागत है! रीडायरेक्ट हो रहा…', mr: 'परत आलात! रीडायरेक्ट होत आहे…', ta: 'மீண்டும் வர வேற்கிறோம்! திருப்பி அனுப்புகிறோம்…', te: 'తిరిగి స్వాగతం! దారి మళ్ళిస్తోంది…' },
  acctCreated:  { en: 'Account created! You can now sign in.', hi: 'खाता बना! अब आप साइन इन कर सकते हैं।', mr: 'खाते तयार! आता साइन इन करा।', ta: 'கணக்கு உருவாக்கப்பட்டது! இப்போது உள்நுழையலாம்.', te: 'ఖాతా సృష్టించబడింది! ఇప్పుడు సైన్ ఇన్ చేయండి.' },
};

/* ── Context ─────────────────────────────────────────────────────────── */
const LangContext = createContext({ lang: 'en', setLang: () => {} });

export function LanguageProvider({ children }) {
  const [lang, setLangState] = useState(() => localStorage.getItem('agro-lang') || 'en');

  const setLang = (l) => {
    setLangState(l);
    localStorage.setItem('agro-lang', l);
  };

  return <LangContext.Provider value={{ lang, setLang }}>{children}</LangContext.Provider>;
}

/* ── Hook ────────────────────────────────────────────────────────────── */
export function useLang() {
  const { lang, setLang } = useContext(LangContext);
  const t = (key) => T[key]?.[lang] ?? T[key]?.en ?? key;
  return { lang, setLang, t };
}
