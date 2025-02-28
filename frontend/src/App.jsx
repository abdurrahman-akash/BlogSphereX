import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainWrapper from './layouts/MainWrapper';
import Home from './views/core/Home';

function App() {
  return (
    <>
      <BrowserRouter>
        <MainWrapper>
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </MainWrapper>
      </BrowserRouter>
    </>
  );
}

export default App;