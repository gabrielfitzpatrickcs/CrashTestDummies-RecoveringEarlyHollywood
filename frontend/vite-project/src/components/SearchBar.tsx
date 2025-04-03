import React, { useState } from "react";
import { MouseEvent } from "react";
import { ChangeEvent } from "react";

interface Props {
    items: string[];
    title: string;
    onSelectHistory: (item: string) => void;
}


function SearchBar({ items, title, onSelectHistory }: Props) {
    const [input, setInput] = useState("")
    let currentSelected = "";

    //Event Handler
    // const handleClick = (e: MouseEvent) => { console.log(item) 
    const handleClick = (item: string) => {
        console.log(item)
        currentSelected = item
        setInput(currentSelected)
    }
    //items = [];

    // const onChange = (e: ChangeEvent, value: string) => {
    //     setInput(e.target.value)
    // }

    return (
        <>
            <div className="input-wrapper m-5">
                {/* <label htmlFor="exampleFormControlInput1" className="form-label text-center">{title}</label> */}
                <h3 className="text-center">View Thousands of Copyright Documents from Early Hollywood</h3>
                <div className="container">
                    {/* <input className="form-control" placeholder="Search for..." value={input} onChange={(e) => setInput(e.target.value)} />
                    <button type="button" className="btn btn-danger" aria-expanded="false">Search</button> */}
                    <form className="d-flex" role="search">
                        <input className="form-control me-2" type="search" placeholder="Search" aria-label="Search" value={input} onChange={(e) => setInput(e.target.value)} />
                        <button className="btn btn-danger" type="submit">Search</button>
                    </form>
                </div>
                <div className="history-list">
                    <ul className="list-group">
                        {items.map((item, index) => (
                            <li
                                className={"list-group-item"}
                                key={item}
                                onClick={() => { handleClick(item) }}
                            >
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            </div >
        </>
    );
}

export default SearchBar