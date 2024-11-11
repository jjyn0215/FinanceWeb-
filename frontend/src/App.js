import React, { Component } from 'react';
import { Route, Routes, Navigate } from "react-router-dom";
import './components/Home'
//import './App.css'
import Dashboard from './Dashboard';
import Home from './components/Home';
import PageNotFound from './components/PageNotFound';

function App() {
  
  return (
    <React.Fragment>
        <main>
            <Routes>
                <Route path="/" element={<PageNotFound />} />
                <Route path="/*" element={<Dashboard />} />
            </Routes>
        </main>
    </React.Fragment> 
  )
}

export default App;