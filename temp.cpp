#include <bits/stdc++.h>
using namespace std;

const int maxn = 10005, maxm = 10005, inf = 0x3f3f3f3f;

int x[maxn], y[maxn], dp[maxn][maxm];
int n, m, k, cnt = 1;
struct node
{
    int p, h, l;
    bool operator<(const node &a) const { return p < a.p; }
} pipes[maxn];

int main()
{
    ios::sync_with_stdio(false);

    cin >> n >> m >> k;
    for (int i = 1; i <= n; i++)
        cin >> x[i] >> y[i];
    for (int i = 1; i <= k; i++)
        cin >> pipes[i].p >> pipes[i].l >> pipes[i].h;
    sort(pipes + 1, pipes + k + 1);

    for (int i = 1; i <= n; i++)
    {
        for (int j = 0; j <= m; j++)
            dp[i % 2][j] = inf;
            
        for (int j = x[i] + 1; j <= x[i] + m; j++)
            dp[i % 2][j] = min(dp[i % 2 ^ 1][j - x[i]] + 1, dp[i % 2][j - x[i]] + 1);
        for (int j = m + 1; j <= x[i] + m; j++)
            dp[i % 2][m] = min(dp[i % 2][m], dp[i % 2][j]);
        for (int j = 1; j <= m - y[i]; j++)
            dp[i % 2][j] = min(dp[i % 2][j], dp[i % 2 ^ 1][j + y[i]]);
        if (i == pipes[cnt].p)
        {
            for (int j = 0; j <= pipes[cnt].l; j++)
                dp[i % 2][j] = inf;
            for (int j = pipes[cnt].h; j <= m; j++)
                dp[i % 2][j] = inf;
            int ans = inf;
            for (int j = 1; j <= m; j++)
                ans = min(dp[i % 2][j], ans);
            if (ans == inf)
                return puts("0"), cout << cnt - 1, 0;
            cnt++;
        }
    }
    int ans = inf;
    for (int j = 1; j <= m; j++)
        ans = min(dp[n % 2][j], ans);
        
    cout << 1 << '\n'
         << ans << endl;
    return 0;
}
