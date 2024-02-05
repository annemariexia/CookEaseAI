import React, { useState } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import LoginForm from './LoginForm';
import InputGoalForm from './InputGoalForm';
import Home from './homePage';
import RecipePage from './recipePage';
import { BrowserRouter as Router, Routes, Switch, Route, Redirect, useNavigate } from 'react-router-dom';



const App = () => {
  const navigate = useNavigate();
  const goToGoalForm = () => navigate('/input_goal');
  const goToHome = () => navigate('/home');
  
  const [loggedIn, setLoggedIn] = useState(false);
  const [inputGoalFormSubmitted, setInputGoalFormSubmitted] = useState(false);
  const [userId, setUserId] = useState(null)
  
  const handleLogin = (user_id) => {
    setLoggedIn(true);
    setUserId(user_id);
  };

  const handleInputGoalFormSubmit = () => {
    setInputGoalFormSubmitted(true);
  };

  

  return (
    <Routes>
      <Route
        path="*"
        element={
          loggedIn ? (
            inputGoalFormSubmitted ? (
              <Home user_id={userId} />
            ) : (
              <Routes>
                <Route
                  path="/input_goal"
                  element={<InputGoalForm onInputGoalFormSubmit={{ handleInputGoalFormSubmit, goToHome }} user_id={userId} />}
                />
              </Routes>
            )
          ) : (
            <LoginForm onLogin={{ handleLogin, goToGoalForm }} />
          )
        }
      />
      <Route path="/recipe_page" element={<RecipePage />} />
    </Routes>
  );
};


export default App;