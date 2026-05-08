import { FormEvent, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router';
import { LogIn, Sparkles, Users } from 'lucide-react';
import { useAuth } from '../auth';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    login();
    navigate(location.pathname === '/login' ? '/' : location.pathname, { replace: true });
  };

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-lg bg-[#68BCE9]">
            <Users size={34} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-[#525659]">SOMAtching</h1>
          <p className="mt-2 text-[#939598]">연수생 탐색을 시작하려면 로그인해주세요</p>
        </div>

        <section className="bg-white rounded-lg border border-gray-200 shadow-md p-8">
          <div className="mb-6 flex items-center gap-2 text-[#525659]">
            <Sparkles size={20} className="text-[#68BCE9]" />
            <h2 className="text-lg font-semibold">로그인</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-[#525659] mb-2">이메일</label>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="example@email.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#525659] mb-2">비밀번호</label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="비밀번호를 입력하세요"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-[#68BCE9] px-5 py-3 font-medium text-white transition-colors hover:bg-[#68BCE9]/90"
            >
              <LogIn size={18} />
              로그인하기
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-[#939598]">
            아직 계정이 없으신가요?{' '}
            <Link to="/signup" className="font-medium text-[#68BCE9] hover:underline">
              회원가입
            </Link>
          </p>
        </section>
      </div>
    </main>
  );
}
