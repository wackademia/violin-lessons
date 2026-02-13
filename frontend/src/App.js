import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Lessons from './pages/Lessons';
import LessonDetail from './pages/LessonDetail';
import Theory from './pages/Theory';
import TheoryDetail from './pages/TheoryDetail';
import Tuner from './pages/Tuner';
import SheetMusic from './pages/SheetMusic';
import SheetMusicDetail from './pages/SheetMusicDetail';
import CareGuides from './pages/CareGuides';
import CareGuideDetail from './pages/CareGuideDetail';
import PracticeScheduler from './pages/PracticeScheduler';
import Bookmarks from './pages/Bookmarks';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="lessons" element={<Lessons />} />
          <Route path="lessons/:id" element={<LessonDetail />} />
          <Route path="theory" element={<Theory />} />
          <Route path="theory/:id" element={<TheoryDetail />} />
          <Route path="tuner" element={<Tuner />} />
          <Route path="sheet-music" element={<SheetMusic />} />
          <Route path="sheet-music/:id" element={<SheetMusicDetail />} />
          <Route path="care" element={<CareGuides />} />
          <Route path="care/:id" element={<CareGuideDetail />} />
          <Route path="practice" element={<PracticeScheduler />} />
          <Route path="bookmarks" element={<Bookmarks />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
