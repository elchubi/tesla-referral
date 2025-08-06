import { useEffect, useState } from 'react'

const images = [
  '/assets/tesla1.jpg',
  '/assets/tesla2.jpg',
  '/assets/tesla3.jpg',
  '/assets/tesla4.jpg'
]

export default function App() {
  const [image, setImage] = useState(images[0])

  useEffect(() => {
    const randomIndex = Math.floor(Math.random() * images.length)
    setImage(images[randomIndex])
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white shadow-2xl rounded-2xl overflow-hidden w-full max-w-3xl">
        <img src={image} alt="Tesla" className="w-full h-80 object-cover" />
        <div className="p-8 text-center">
          <h1 className="text-4xl font-bold text-red-600 mb-4">¡Usa mi código de referido Tesla!</h1>
          <p className="text-lg text-gray-700 mb-6">
            Benefíciate tú y yo con recompensas exclusivas al ordenar tu nuevo Tesla.
          </p>
          <a
            href="https://ts.la/davidanton806840"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-red-500 hover:bg-red-600 text-white font-semibold px-6 py-3 rounded-xl transition"
          >
            Ir al sitio de Tesla
          </a>
        </div>
      </div>
    </div>
  )
}
