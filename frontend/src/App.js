import React, { Component } from 'react';
import { Route, Routes, Navigate } from "react-router-dom";
import './components/Home'
//import './App.css'
import Home from './components/Home';


function App() {
  
  return (
    <React.Fragment>
        <main>
            <Routes>
                <Route path="/" element={<Home />} />
            </Routes>
        </main>
    </React.Fragment> 
  )
}

export default App;