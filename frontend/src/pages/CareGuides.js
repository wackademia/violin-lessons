import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Sparkles, Wrench as WrenchIcon, Ruler, Home, Wand } from 'lucide-react';
import { api } from '../utils/api';

const iconMap = {
  sparkles: Sparkles,
  wand: Wand,
  wrench: WrenchIcon,
  ruler: Ruler,
  home: Home,
};

export default function CareGuides() {
  const [guides, setGuides] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCareGuides().then(setGuides).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8" data-testid="care-guides-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-stone-100">Care & Maintenance</h1>
        <p className="text-stone-400 font-body text-sm mt-2">Keep your violin in perfect condition</p>
      </div>

      {/* Hero image */}
      <div className="relative rounded-2xl overflow-hidden h-48 md:h-64">
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent z-10" />
        <img
          src="https://images.unsplash.com/photo-1566913485314-2246e21e3234?w=800&q=80"
          alt="Violin care"
          className="w-full h-full object-cover"
        />
        <div className="absolute bottom-4 left-6 z-20">
          <p className="text-stone-300 font-body text-sm">Proper care extends the life and sound of your instrument</p>
        </div>
      </div>

      {loading ? (
        <div className="text-stone-500 text-center py-12">Loading...</div>
      ) : (
        <div className="space-y-3" data-testid="care-guides-list">
          {guides.map((guide) => {
            const Icon = iconMap[guide.icon] || Sparkles;
            return (
              <Link
                key={guide.id}
                to={`/care/${guide.id}`}
                data-testid={`care-card-${guide.id}`}
                className="group flex items-center gap-4 p-5 rounded-2xl bg-background-secondary border border-stone-800 hover:border-primary/30 transition-all duration-300"
              >
                <div className="w-11 h-11 rounded-xl bg-stone-800 flex items-center justify-center text-amber-400 shrink-0">
                  <Icon size={20} strokeWidth={1.5} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-body font-semibold text-stone-200 text-sm group-hover:text-primary transition-colors">{guide.title}</h3>
                  <p className="text-stone-500 text-xs mt-0.5">{guide.description}</p>
                </div>
                <ChevronRight size={16} className="text-stone-600 group-hover:text-primary transition-colors shrink-0" />
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
