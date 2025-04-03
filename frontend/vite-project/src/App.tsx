import ListGroup from './components/ListGroup'
import NavBar from './components/NavBar'
import SearchBar from './components/SearchBar'
import InformationBelowSearchbar from './components/InformationBelowSearchbar'
import DropDown from './components/DropDown'

function App() {
  let items = ["search history", "item1", "item2", "item3"]

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
        <div className="container">
          <div className="row">
            <div className="col d-flex justify-content-end">
              <DropDown items={items} title='Filter by Actor' />
            </div>
            <div className="col d-flex justify-content-center">
              <DropDown items={items} title='Filter by Year' />
            </div>
            <div className="col d-flex justify-content-start">
              <DropDown items={items} title='Filter by Doc Type' />
            </div>
          </div>
        </div>
        <InformationBelowSearchbar />
      </div>
    </>
  )
}

export default App
