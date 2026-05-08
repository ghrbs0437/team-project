import { useState } from 'react';
import { Link } from 'react-router';
import { UserPlus, Sparkles } from 'lucide-react';

export default function Signup() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: '',
    mbti: '',
    age: '',
    status: '',
    location: '',
    stack: '',
    hoursPerWeek: '',
    interests: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  return (
    <div className="min-h-full bg-gray-50 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-[#68BCE9] rounded-full mb-4">
            <UserPlus size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-[#525659] mb-2">회원가입</h1>
          <p className="text-[#939598]">SOMAtching에서 함께할 팀원을 찾을 준비를 해보세요</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Info Section */}
            <div>
              <h2 className="text-lg font-semibold text-[#525659] mb-4 flex items-center gap-2">
                <div className="w-6 h-6 bg-[#68BCE9] text-white rounded-full flex items-center justify-center text-xs">1</div>
                기본 정보
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">이름</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="홍길동"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">이메일</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="example@email.com"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">비밀번호</label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">비밀번호 확인</label>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Profile Info Section */}
            <div className="pt-6 border-t border-gray-200">
              <h2 className="text-lg font-semibold text-[#525659] mb-4 flex items-center gap-2">
                <div className="w-6 h-6 bg-[#68BCE9] text-white rounded-full flex items-center justify-center text-xs">2</div>
                프로필 정보
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">역할</label>
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  >
                    <option value="">선택해주세요</option>
                    <option value="Frontend Developer">Frontend Developer</option>
                    <option value="Backend Developer">Backend Developer</option>
                    <option value="Full-stack Developer">Full-stack Developer</option>
                    <option value="UI/UX Designer">UI/UX Designer</option>
                    <option value="DevOps Engineer">DevOps Engineer</option>
                    <option value="Data Scientist">Data Scientist</option>
                    <option value="Mobile Developer">Mobile Developer</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">MBTI</label>
                  <input
                    type="text"
                    name="mbti"
                    value={formData.mbti}
                    onChange={handleChange}
                    placeholder="예: ENFJ"
                    maxLength={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">나이</label>
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    placeholder="25"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">학력 상태</label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  >
                    <option value="">선택해주세요</option>
                    <option value="학부 재학">학부 재학</option>
                    <option value="학부 졸업">학부 졸업</option>
                    <option value="대학원 재학">대학원 재학</option>
                    <option value="대학원 졸업">대학원 졸업</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">지역</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="서울, 한국"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">주간 활동 시간</label>
                  <select
                    name="hoursPerWeek"
                    value={formData.hoursPerWeek}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  >
                    <option value="">선택해주세요</option>
                    <option value="10-20">10-20시간</option>
                    <option value="20-30">20-30시간</option>
                    <option value="30-35">30-35시간</option>
                    <option value="35-40">35-40시간</option>
                    <option value="40+">40시간 이상</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Skills & Interests Section */}
            <div className="pt-6 border-t border-gray-200">
              <h2 className="text-lg font-semibold text-[#525659] mb-4 flex items-center gap-2">
                <div className="w-6 h-6 bg-[#68BCE9] text-white rounded-full flex items-center justify-center text-xs">3</div>
                기술 스택 & 관심사
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">기술 스택</label>
                  <input
                    type="text"
                    name="stack"
                    value={formData.stack}
                    onChange={handleChange}
                    placeholder="예: React, TypeScript, Node.js (쉼표로 구분)"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                  <p className="text-xs text-[#939598] mt-1">주요 기술 스택을 쉼표로 구분하여 입력해주세요</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#525659] mb-2">관심사 & 프로젝트 선호도</label>
                  <textarea
                    name="interests"
                    value={formData.interests}
                    onChange={handleChange}
                    placeholder="예: 스타트업, AI/ML, 오픈소스 프로젝트 등"
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Matching Info */}
            <div className="bg-[#68BCE9]/10 border border-[#68BCE9]/30 rounded-lg p-4">
              <div className="flex items-start gap-2">
                <Sparkles size={20} className="text-[#68BCE9] mt-0.5 flex-shrink-0" />
                <div className="text-sm text-[#525659]">
                  작성하신 정보는 팀원 탐색과 프로필 소개에 활용됩니다.
                  관심 분야와 기술 스택을 구체적으로 적을수록 함께할 팀원을 찾기 쉬워집니다.
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-6 flex gap-4">
              <Link
                to="/"
                className="flex-1 px-6 py-3 border border-gray-300 text-[#525659] rounded-lg hover:bg-gray-50 transition-colors text-center"
              >
                취소
              </Link>
              <button
                type="submit"
                className="flex-1 px-6 py-3 bg-[#68BCE9] text-white rounded-lg hover:bg-[#68BCE9]/90 transition-colors font-medium"
              >
                회원가입 완료
              </button>
            </div>
          </form>
        </div>

        {/* Login Link */}
        <div className="text-center mt-6">
          <p className="text-[#939598]">
            이미 계정이 있으신가요?{' '}
            <Link to="/" className="text-[#68BCE9] hover:underline">
              로그인하기
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
