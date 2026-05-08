import { useState } from 'react';
import { User, Edit2, Save, X } from 'lucide-react';

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    name: '홍길동',
    email: 'hong@email.com',
    role: 'Frontend Developer',
    mbti: 'ENFJ',
    age: '25',
    status: '학부 재학',
    location: '서울, 한국',
    stack: 'React, TypeScript, Next.js, Tailwind CSS',
    hoursPerWeek: '40+',
    interests: '스타트업, 오픈소스 프로젝트, AI/ML 기술 학습에 관심이 많습니다. 협업과 커뮤니케이션을 중요하게 생각하며, 새로운 도전을 즐깁니다.'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = () => {
    console.log('Profile updated:', profileData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  return (
    <div className="min-h-full bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-[#68BCE9] flex items-center justify-center">
                <User size={40} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-[#525659]">{profileData.name}</h1>
                <p className="text-[#939598]">{profileData.email}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="px-3 py-1 bg-[#68BCE9]/20 text-[#68BCE9] text-sm rounded-full">
                    {profileData.role}
                  </span>
                  <span className="px-3 py-1 bg-gray-100 text-[#525659] text-sm rounded-full">
                    MBTI: {profileData.mbti}
                  </span>
                </div>
              </div>
            </div>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 px-4 py-2 bg-[#68BCE9] text-white rounded-lg hover:bg-[#68BCE9]/90 transition-colors"
              >
                <Edit2 size={18} />
                프로필 수정
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={handleCancel}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-[#525659] rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <X size={18} />
                  취소
                </button>
                <button
                  onClick={handleSave}
                  className="flex items-center gap-2 px-4 py-2 bg-[#68BCE9] text-white rounded-lg hover:bg-[#68BCE9]/90 transition-colors"
                >
                  <Save size={18} />
                  저장
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Profile Details */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-xl font-semibold text-[#525659] mb-6">상세 정보</h2>

          <div className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">이름</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="name"
                    value={profileData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                  />
                ) : (
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#525659]">{profileData.name}</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">이메일</label>
                <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#939598]">{profileData.email}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">역할</label>
                {isEditing ? (
                  <select
                    name="role"
                    value={profileData.role}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                  >
                    <option value="Frontend Developer">Frontend Developer</option>
                    <option value="Backend Developer">Backend Developer</option>
                    <option value="Full-stack Developer">Full-stack Developer</option>
                    <option value="UI/UX Designer">UI/UX Designer</option>
                    <option value="DevOps Engineer">DevOps Engineer</option>
                    <option value="Data Scientist">Data Scientist</option>
                    <option value="Mobile Developer">Mobile Developer</option>
                  </select>
                ) : (
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#525659]">{profileData.role}</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">MBTI</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="mbti"
                    value={profileData.mbti}
                    onChange={handleChange}
                    maxLength={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                  />
                ) : (
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#525659]">{profileData.mbti}</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">나이</label>
                {isEditing ? (
                  <input
                    type="number"
                    name="age"
                    value={profileData.age}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                  />
                ) : (
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#525659]">{profileData.age}세</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">학력 상태</label>
                {isEditing ? (
                  <select
                    name="status"
                    value={profileData.status}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                  >
                    <option value="학부 재학">학부 재학</option>
                    <option value="학부 졸업">학부 졸업</option>
                    <option value="대학원 재학">대학원 재학</option>
                    <option value="대학원 졸업">대학원 졸업</option>
                  </select>
                ) : (
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#525659]">{profileData.status}</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">지역</label>
                {isEditing ? (
                  <input
                    type="text"
                    name="location"
                    value={profileData.location}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                  />
                ) : (
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#525659]">{profileData.location}</div>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-[#525659] mb-2">주간 활동 시간</label>
                {isEditing ? (
                  <select
                    name="hoursPerWeek"
                    value={profileData.hoursPerWeek}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                  >
                    <option value="10-20">10-20시간</option>
                    <option value="20-30">20-30시간</option>
                    <option value="30-35">30-35시간</option>
                    <option value="35-40">35-40시간</option>
                    <option value="40+">40시간 이상</option>
                  </select>
                ) : (
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-[#525659]">{profileData.hoursPerWeek}시간</div>
                )}
              </div>
            </div>

            {/* Tech Stack */}
            <div className="pt-6 border-t border-gray-200">
              <label className="block text-sm font-medium text-[#525659] mb-2">기술 스택</label>
              {isEditing ? (
                <input
                  type="text"
                  name="stack"
                  value={profileData.stack}
                  onChange={handleChange}
                  placeholder="예: React, TypeScript, Node.js (쉼표로 구분)"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                />
              ) : (
                <div className="flex flex-wrap gap-2">
                  {profileData.stack.split(',').map((tech, index) => (
                    <span key={index} className="px-3 py-1 bg-gray-100 text-[#525659] text-sm rounded-full">
                      {tech.trim()}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Interests */}
            <div className="pt-6 border-t border-gray-200">
              <label className="block text-sm font-medium text-[#525659] mb-2">관심사 & 프로젝트 선호도</label>
              {isEditing ? (
                <textarea
                  name="interests"
                  value={profileData.interests}
                  onChange={handleChange}
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#68BCE9]"
                />
              ) : (
                <div className="px-4 py-3 bg-gray-50 rounded-lg text-[#525659]">{profileData.interests}</div>
              )}
            </div>
          </div>
        </div>

        {/* Activity Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-[#68BCE9] mb-2">24</div>
            <div className="text-sm text-[#939598]">등록된 관심사</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-[#68BCE9] mb-2">8</div>
            <div className="text-sm text-[#939598]">기술 스택</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-3xl font-bold text-[#68BCE9] mb-2">156</div>
            <div className="text-sm text-[#939598]">프로필 방문</div>
          </div>
        </div>
      </div>
    </div>
  );
}
