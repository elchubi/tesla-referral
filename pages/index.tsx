import { useEffect, useState } from "react";

export default function HomePage() {
  const [images, setImages] = useState<any[]>([]);
  const [index, setIndex] = useState(0);
  const [lang, setLang] = useState("en");
  const [country, setCountry] = useState<string | null>(null);

  const IMAGES_JSON = "/assets/galeria.json";
  const REFERRAL_URL = "https://ts.la/davidanton806840";

  useEffect(() => {
    fetch(IMAGES_JSON)
      .then((res) => res.json())
      .then((data) => setImages(data));

    const langHeader = navigator.language || "en";
    setLang(langHeader.startsWith("es") ? "es" : "en");

    fetch("https://ipapi.co/json")
      .then((res) => res.json())
      .then((data) => setCountry(data.country));
  }, []);

  const promoText: Record<string, any> = {
    es: {
      MX: "Obtén 1 año de supercarga gratis al comprar tu Tesla con este código:",
      default: "Obtén 3 meses de FSD o $400 USD en solar usando mi código Tesla:",
      button: "Usar mi código de referido",
    },
    en: {
      US: "Get 3 months of Full Self-Driving (Supervised) or $400 off Solar with my Tesla referral:",
      default: "Use my referral to get exclusive Tesla benefits:",
      button: "Use my Tesla referral code",
    },
  };

  const t = promoText[lang][country] || promoText[lang].default;
  const button = promoText[lang].button;
  const currentImage = images[index];

  const nextImage = () => setIndex((i) => (i + 1) % images.length);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white p-4">
      <h1 className="text-3xl md:text-5xl font-bold text-center mb-4">{t}</h1>

      <button
        className="mb-6 text-lg px-6 py-3 bg-white text-black rounded-xl font-semibold hover:bg-gray-200"
        onClick={() => window.open(REFERRAL_URL, "_blank")}
      >
        {button}
      </button>

      {currentImage && (
        <div className="w-full max-w-4xl bg-white text-black rounded-xl overflow-hidden cursor-pointer" onClick={nextImage}>
          <img
            src={`/assets/${currentImage.filename}`}
            alt="Tesla Promo"
            className="w-full"
          />
        </div>
      )}
    </div>
  );
}
