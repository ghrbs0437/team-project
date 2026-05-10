import { FormEvent, useEffect, useState } from 'react';
import { ExternalLink, FileText, Loader2, RefreshCw, Search, User } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const PAGE_SIZE = 20;

type CrawledProfileSummary = {
  id: number;
  name: string;
  tags: string[];
};

type CrawledProfileDetail = CrawledProfileSummary & {
  title?: string;
  source?: string;
  source_url?: string;
  raw_text?: string;
  created_at?: string;
  updated_at?: string;
};

type CrawledProfilesResponse = {
  crawled_profiles: RawCrawledProfile[];
  page?: number;
  size?: number;
  total?: number;
  has_next?: boolean;
};

type RawCrawledProfile = {
  id?: number | string;
  profile_id?: number | string;
  name?: string;
  title?: string;
  source?: string;
  source_url?: string;
  raw_text?: string;
  parsed_json?: {
    tags?: unknown;
    [key: string]: unknown;
  } | null;
  tags?: unknown;
  created_at?: string;
  updated_at?: string;
};

function normalizeTags(tags: unknown): string[] {
  return Array.isArray(tags) ? tags.filter((tag): tag is string => typeof tag === 'string') : [];
}

function getDisplayTags(profile: RawCrawledProfile): string[] {
  return normalizeTags(profile.parsed_json?.tags ?? profile.tags);
}

function normalizeSummary(profile: RawCrawledProfile): CrawledProfileSummary {
  return {
    id: Number(profile.id ?? profile.profile_id),
    name: profile.title ?? profile.name ?? '이름 없음',
    tags: getDisplayTags(profile),
  };
}

function normalizeDetail(profile: RawCrawledProfile): CrawledProfileDetail {
  return {
    ...profile,
    id: Number(profile.id ?? profile.profile_id),
    name: profile.title ?? profile.name ?? '이름 없음',
    tags: getDisplayTags(profile),
  };
}

function normalizeProfilesResponse(
  data: CrawledProfilesResponse | RawCrawledProfile[],
  requestedPage: number,
  previousCount: number,
) {
  if (Array.isArray(data)) {
    const crawledProfiles = data.map(normalizeSummary);

    return {
      crawledProfiles,
      page: requestedPage,
      total: previousCount + crawledProfiles.length,
      hasNext: crawledProfiles.length === PAGE_SIZE,
    };
  }

  const crawledProfiles = (data.crawled_profiles ?? []).map(normalizeSummary);

  return {
    crawledProfiles,
    page: data.page ?? requestedPage,
    total: data.total ?? previousCount + crawledProfiles.length,
    hasNext: Boolean(data.has_next),
  };
}

function buildUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(path, API_BASE_URL);

  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      url.searchParams.set(key, String(value));
    }
  });

  return url.toString();
}

async function fetchJson<T>(url: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(url);
  } catch {
    throw new Error('연수생 정보를 가져오는 데 시간이 걸리고 있어요. 잠시 후 다시 시도해주세요.');
  }

  if (!response.ok) {
    throw new Error('연수생 정보를 가져오는 데 시간이 걸리고 있어요. 잠시 후 다시 시도해주세요.');
  }

  return response.json() as Promise<T>;
}

export default function Dashboard() {
  const [profiles, setProfiles] = useState<CrawledProfileSummary[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<CrawledProfileDetail | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const loadProfiles = async (nextPage = 1, append = false) => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      const endpoint = submittedQuery ? '/crawled-profiles/embedded' : '/crawled-profiles';
      const params: Record<string, string | number> = {
        page: nextPage,
        size: PAGE_SIZE,
      };
      if (submittedQuery) {
        params.context = submittedQuery;
      }

      const data = await fetchJson<CrawledProfilesResponse | RawCrawledProfile[]>(
        buildUrl(endpoint, params),
      );
      const { crawledProfiles, page, total, hasNext } = normalizeProfilesResponse(
        data,
        nextPage,
        append ? profiles.length : 0,
      );

      setProfiles((prev) => (append ? [...prev, ...crawledProfiles] : crawledProfiles));
      setPage(page);
      setTotal(total);
      setHasNext(hasNext);

      if (!append) {
        setSelectedProfile(null);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '연수생 정보를 가져오지 못했어요.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadProfileDetail = async (profileId: number) => {
    setIsDetailLoading(true);
    setErrorMessage('');

    try {
      const data = await fetchJson<RawCrawledProfile>(buildUrl(`/crawled-profiles/${profileId}`));
      setSelectedProfile(normalizeDetail(data));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '연수생 상세 정보를 가져오지 못했어요.');
    } finally {
      setIsDetailLoading(false);
    }
  };

  useEffect(() => {
    void loadProfiles(1, false);
  }, [submittedQuery]);

  const handleSearch = (event: FormEvent) => {
    event.preventDefault();
    setSubmittedQuery(searchInput.trim());
  };

  const handleRefresh = () => {
    void loadProfiles(1, false);
  };

  const handleLoadMore = () => {
    if (!isLoading && hasNext) {
      void loadProfiles(page + 1, true);
    }
  };

  return (
    <div className="min-h-full bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <section className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center gap-2 text-[#68BCE9]">
                <FileText size={22} />
                <h2 className="text-xl font-semibold">연수생 탐색</h2>
              </div>
              <p className="mt-1 text-sm text-[#939598]">
                원하는 요구사항을 입력하면 AI가 가장 적합한 연수생을 찾아줍니다.
              </p>
            </div>
            <form onSubmit={handleSearch} className="flex w-full gap-2 md:w-auto">
              <div className="relative min-w-0 flex-1 md:w-80">
                <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#939598]" />
                <input
                  type="text"
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="원하는 연수생의 특징이나 요구사항을 입력해보세요"
                  className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-[#68BCE9]/30"
                />
              </div>
              <button
                type="submit"
                className="rounded-lg bg-[#525659] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#525659]/90"
              >
                검색
              </button>
              <button
                type="button"
                onClick={handleRefresh}
                className="rounded-lg border border-gray-300 px-3 py-2 text-[#525659] transition-colors hover:bg-gray-50"
                aria-label="새로고침"
              >
                <RefreshCw size={18} />
              </button>
            </form>
          </div>

          <div className="flex items-center justify-between border-t border-gray-100 pt-4">
            <h3 className="text-sm font-medium text-gray-900">
              {isLoading && profiles.length === 0
                ? '연수생 정보를 불러오는 중'
                : submittedQuery
                  ? `검색 결과 ${profiles.length}명 / 총 ${total}명`
                  : `총 ${total}명`}
            </h3>
            <span className="text-xs text-[#939598]">AI가 분석한 추천 결과를 확인해보세요</span>
          </div>

          {errorMessage && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorMessage}
            </div>
          )}
        </section>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
          <section className="grid grid-cols-1 gap-4">
            {isLoading && profiles.length === 0 && (
              <div className="flex items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white p-10 text-sm text-[#939598]">
                <Loader2 size={18} className="animate-spin" />
                연수생 정보를 불러오는 중입니다.
              </div>
            )}

            {!isLoading && profiles.length === 0 && (
              <div className="rounded-lg border border-dashed border-gray-300 bg-white p-10 text-center text-sm text-[#939598]">
                검색 결과가 없습니다.
              </div>
            )}

            {profiles.map((profile) => (
              <article
                key={profile.id}
                className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                  <div className="flex items-start gap-3">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#68BCE9]/15">
                      <User size={22} className="text-[#68BCE9]" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-[#525659]">{profile.name}</h4>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {profile.tags.map((tag) => (
                          <span
                            key={tag}
                            className="rounded-full bg-gray-100 px-3 py-1 text-xs text-[#525659]"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => void loadProfileDetail(profile.id)}
                    className="rounded border border-[#68BCE9] px-4 py-2 text-sm font-medium text-[#68BCE9] transition-colors hover:bg-[#68BCE9] hover:text-white"
                  >
                    상세 보기
                  </button>
                </div>
              </article>
            ))}

            {hasNext && (
              <div className="flex justify-center pt-2">
                <button
                  type="button"
                  onClick={handleLoadMore}
                  disabled={isLoading}
                  className="rounded-lg border border-gray-300 px-6 py-3 text-[#525659] transition-colors hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isLoading ? '불러오는 중' : '더 보기'}
                </button>
              </div>
            )}
          </section>

          <aside className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm lg:sticky lg:top-6 lg:self-start">
            {isDetailLoading ? (
              <div className="flex items-center gap-2 text-sm text-[#939598]">
                <Loader2 size={18} className="animate-spin" />
                자세한 정보를 불러오는 중입니다.
              </div>
            ) : selectedProfile ? (
              <div className="space-y-5">
                <div>
                  <div className="text-xs font-medium text-[#939598]">연수생 소개</div>
                  <h3 className="mt-2 text-xl font-semibold text-[#525659]">{selectedProfile.name}</h3>
                  {selectedProfile.title && <p className="mt-1 text-sm text-[#939598]">{selectedProfile.title}</p>}
                </div>

                <div className="flex flex-wrap gap-2">
                  {selectedProfile.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-gray-100 px-3 py-1 text-xs text-[#525659]">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="space-y-3 border-t border-gray-100 pt-4 text-sm">
                  {selectedProfile.source && (
                    <div>
                      <div className="mb-1 text-xs font-medium text-[#939598]">출처</div>
                      <div className="text-[#525659]">{selectedProfile.source}</div>
                    </div>
                  )}
                  {selectedProfile.source_url && (
                    <div>
                      <div className="mb-1 text-xs font-medium text-[#939598]">원본 링크</div>
                      <a
                        href={'https://www.notion.so'+selectedProfile.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 break-all text-[#68BCE9] hover:underline"
                      >
                        {selectedProfile.source_url}
                        <ExternalLink size={14} />
                      </a>
                    </div>
                  )}
                  {selectedProfile.raw_text && (
                    <div>
                      <div className="mb-1 text-xs font-medium text-[#939598]">소개 원문</div>
                      <p className="leading-6 text-[#525659]">{selectedProfile.raw_text}</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-sm text-[#939598]">목록에서 연수생을 선택하면 자세한 정보를 볼 수 있습니다.</div>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}
