import { Outlet, Link, useLocation } from 'react-router';
import { LogOut, Search, User, Users, UserCircle, Settings } from 'lucide-react';
import { useAuth } from '../auth';

export default function Root() {
  const location = useLocation();
  const { logout } = useAuth();

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="size-full flex bg-white">
      {/* Sidebar */}
      <aside className="w-16 bg-[#525659] flex flex-col items-center py-6 gap-8">
        <div className="text-white font-bold text-sm">SM</div>
        <nav className="flex flex-col gap-6">
          <Link
            to="/"
            className={`transition-colors p-2 rounded ${
              isActive('/') && location.pathname === '/'
                ? 'text-white bg-white/10'
                : 'text-white/60 hover:text-white/90'
            }`}
          >
            <Users size={24} />
          </Link>
          <Link
            to="/profile"
            className={`transition-colors p-2 rounded ${
              isActive('/profile')
                ? 'text-white bg-white/10'
                : 'text-white/60 hover:text-white/90'
            }`}
          >
            <UserCircle size={24} />
          </Link>
          <button className="text-white/60 hover:text-white/90 transition-colors p-2">
            <Settings size={24} />
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Utility Bar */}
        <header className="h-16 border-b border-gray-200 flex items-center justify-between px-8">
          <div className="text-xl font-semibold text-[#525659]">SOMAtching</div>
          <div className="flex items-center gap-6">
            <button className="text-[#939598] hover:text-[#525659] transition-colors">
              <Search size={20} />
            </button>
            <Link to="/profile" className="flex items-center gap-2 text-gray-700 hover:text-[#525659] transition-colors">
              <div className="w-8 h-8 rounded-full bg-[#68BCE9]/20 flex items-center justify-center">
                <User size={16} className="text-[#68BCE9]" />
              </div>
              <span className="text-sm">홍길동</span>
            </Link>
            <button
              onClick={logout}
              className="flex items-center gap-2 text-sm text-[#939598] hover:text-[#525659] transition-colors"
            >
              <LogOut size={18} />
              로그아웃
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
