import './App.css'
import PgnViewer from './components/PgnViewer'

function App() {
  return (
    <div className="app-layout">
      <header className="app-header">
        <h1 className="logo">
          Chess Speak <span className="highlight">Out Loud</span>
        </h1>
      </header>
      
      <main className="main-content">
        <PgnViewer />
      </main>
    </div>
  )
}

export default App
