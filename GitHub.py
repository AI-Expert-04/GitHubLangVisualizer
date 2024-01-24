import requests
import matplotlib.pyplot as plt


# GitHub API를 사용하여 조직의 레포지토리에서 사용된 언어 데이터 수집
def fetch_languages(url, headers, programming_languages):
    languages = {}
    while True:
        response = requests.get(url, headers=headers)
        repos = response.json()
        if response.status_code != 200 or not repos:
            break

        for repo in repos:
            repo_languages = requests.get(repo['languages_url'], headers=headers).json()
            for lang, bytes in repo_languages.items():
                if lang in programming_languages:
                    if lang in languages:
                        languages[lang] += bytes
                    else:
                        languages[lang] = bytes
        # 페이지네이션 처리
        if 'next' in response.links:
            url = response.links['next']['url']
        else:
            break
    return languages


def create_gauge_bars(languages, title, filename):
    # 프로그래밍 언어별 색상 정의
    language_colors = {
        'Python': '#3572A5', 'Java': '#b07219', 'JavaScript': '#f1e05a', 'C++': '#f34b7d', 'C#': '#178600',
        'Ruby': '#701516', 'Go': '#00ADD8', 'TypeScript': '#2b7489', 'PHP': '#4F5D95', 'Swift': '#ffac45',
        'Kotlin': '#F18E33', 'Objective-C': '#438eff',
    }
    total_bytes = sum(languages.values())
    languages_percent = {lang: (bytes / total_bytes) * 100 for lang, bytes in languages.items() if bytes > 0}
    fig, ax = plt.subplots()
    languages_sorted = sorted(languages_percent.items(), key=lambda item: item[1], reverse=True)
    for i, (lang, percent) in enumerate(languages_sorted):
        ax.barh(lang, percent, color=language_colors.get(lang, 'grey'))
        ax.text(percent, i, f' {percent:.1f}%', va='center')

    plt.xlabel('Percentage of Code (%)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


if __name__ == '__main__':
    org_name = 'Kkuing-Team-Project'
    user_name = 'AI-Expert-04'  # GitHub 사용자 이름으로 교체
    token = ''

    programming_languages = [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go',
        'TypeScript', 'PHP', 'Swift', 'Kotlin', 'Objective-C'
    ]

    # headers = {'Authorization': f'{token}'}
    headers = {'Authorization': f'{token}'}
    # 조직 리포지토리의 언어 데이터 수집 및 시각화
    org_url = f'https://api.github.com/orgs/{org_name}/repos?type=all/'
    org_languages = fetch_languages(org_url, headers, programming_languages)
    create_gauge_bars(org_languages, f'Programming Language Usage in {org_name} Organization',
                      f'{org_name}_language_usage.png')

    # 개인 리포지토리의 언어 데이터 수집 및 시각화
    user_url = f'https://api.github.com/users/{user_name}/repos?type=all'
    user_languages = fetch_languages(user_url, headers, programming_languages)
    create_gauge_bars(user_languages, f'Programming Language Usage in {user_name} Repositories',
                      f'{user_name}_language_usage.png')

    # 조직과 개인 리포지토리의 언어 데이터를 합쳐 시각화
    combined_languages = {lang: org_languages.get(lang, 0) + user_languages.get(lang, 0) for lang in
                          set(org_languages) | set(user_languages)}
    create_gauge_bars(combined_languages, f'Combined Programming Language Usage in {org_name} + {user_name}',
                      'combined_language_usage.png')
