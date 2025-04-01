import React, { useState } from "react";
import { MouseEvent } from "react";
import { ChangeEvent } from "react";

interface SearchBarProps {
    items: string[];
    title: string;
    onSelectHistory: (item: string) => void;
}


function SearchBar({ items, title, onSelectHistory }: SearchBarProps) {
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
                <label htmlFor="exampleFormControlInput1" className="form-label">{title}</label>
                <input className="form-control" placeholder="Search the archive" value={input} onChange={(e) => setInput(e.target.value)} />
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