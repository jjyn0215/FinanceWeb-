import React, { Component } from 'react';
import { Route, Routes, Navigate } from "react-router-dom";
import './components/Home'
//import './App.css'
import Dashboard from './Dashboard';
import Home from './components/Home';
import PageNotFound from './components/PageNotFound';
import SignIn from './components/SignIn';
import SignUp from './components/SignUp'
import { useLocation } from 'react-router-dom';

function App() {
  const location = useLocation();
  return (
    <React.Fragment>
        <main>
            <Routes key={location.pathname} location={location}>
                <Route path="/*" element={<Navigate to="/SignIn" replace />} />
                <Route path="/404" element={<PageNotFound />} />
                <Route path="/Chart/:ticker" element={<Dashboard />} />
                <Route path="/Chart/" element={<Navigate to="/*" replace />} />
                <Route path="/SignIn" element={<SignIn />} />
                <Route path="/SignIn/*" element={<Navigate to="/SignIn" replace />} />
                <Route path="/SignUp" element={<SignUp />} />
                <Route path="/SignUp/*" element={<Navigate to="/SignUp" replace />} />
            </Routes>
        </main>
    </React.Fragment> 
  )
}

export default App;