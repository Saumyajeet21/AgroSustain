import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { Leaf, Sprout, Stethoscope, BarChart3, MessageSquare } from 'lucide-react';
import Landing from './pages/Landing';
import CropPredictor from './pages/CropPredictor';
import PlantDoctor from './pages/PlantDoctor';
import Economics from './pages/Economics';
import Chatbot from './pages/Chatbot';
import './index.css';

function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        <span className="brand-dot"></span>
        AgroSustain
      </NavLink>
      <ul className="navbar-links">
        <li>
          <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
            <Leaf size={15} /> Home
          </NavLink>
        </li>
        <li>
          <NavLink to="/predict" className={({ isActive }) => isActive ? 'active' : ''}>
            <Sprout size={15} /> Crop Advisor
          </NavLink>
        </li>
        <li>
          <NavLink to="/doctor" className={({ isActive }) => isActive ? 'active' : ''}>
            <Stethoscope size={15} /> Plant Doctor
          </NavLink>
        </li>
        <li>
          <NavLink to="/economics" className={({ isActive }) => isActive ? 'active' : ''}>
            <BarChart3 size={15} /> Economics
          </NavLink>
        </li>
        <li>
          <NavLink to="/chat" className={({ isActive }) => isActive ? 'active' : ''}>
            <MessageSquare size={15} /> AgroBot
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="bg-orbs" />
      <Navbar />
      <Routes>
        <Route path="/"          element={<Landing />} />
        <Route path="/predict"   element={<CropPredictor />} />
        <Route path="/doctor"    element={<PlantDoctor />} />
        <Route path="/economics" element={<Economics />} />
        <Route path="/chat"      element={<Chatbot />} />
      </Routes>
    </BrowserRouter>
  );
}
