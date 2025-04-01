import ListGroup from './components/ListGroup'
import NavBar from './components/NavBar'
import SearchBar from './components/SearchBar'
import InformationBelowSearchbar from './components/InformationBelowSearchbar'

function App() {
  let items = ["search", "item1", "item2", "item3"]

  const handleSelectHistory = (item: string) => {
    console.log(item);
  }

  return (
    <>
      <div>
        <NavBar />
        <div className="container">
          <SearchBar items={items} title='Search Bar' onSelectHistory={handleSelectHistory} />
        </div>
        <InformationBelowSearchbar />
      </div>
    </>
  )
}

export default App
