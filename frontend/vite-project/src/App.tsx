import ListGroup from './components/ListGroup'
import NavBar from './components/NavBar'
import SearchBar from './components/SearchBar'
import InformationBelowSearchbar from './components/InformationBelowSearchbar'

function App() {

  return (
    <>
      <div>
        <NavBar />
        <div className="container">
          <SearchBar />
        </div>
        <InformationBelowSearchbar />
      </div>
    </>
  )
}

export default App
