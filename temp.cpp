#include <bits/stdc++.h>
using namespace std;
int v[100010], l[100010], r[100010], d[100010], L[100010], n, head[100010], tot, heap[100010], sz[100010];
long long sum[100010];
struct ed
{
    int nxt, to;
} e[100010];
int m;
long long ans;
void add(int u, int v)
{
    e[++tot].nxt = head[u];
    e[tot].to = v;
    head[u] = tot;
}
int merge(int x, int y)
{
    if (!x || !y)
        return x + y;
    if (v[x] < v[y])
        swap(x, y);
    r[x] = merge(r[x], y);
    if (d[r[x]] > d[l[x]])
        swap(r[x], l[x]);
    d[x] = d[r[x]] + 1;
    return x;
}
void dfs(int u)
{
    heap[u] = u;
    sum[u] = v[u];
    sz[u] = 1;
    for (int i = head[u]; i != -1; i = e[i].nxt)
    {
        int v = e[i].to;
        dfs(v);
        sum[u] += sum[v];
        sz[u] += sz[v];
        heap[u] = merge(heap[u], heap[v]);
    }
    while (sum[u] > m && sz[u])
    {
        sum[u] -= v[heap[u]];
        heap[u] = merge(r[heap[u]], l[heap[u]]);
        sz[u]--;
    }
    ans = max(ans, (long long)sz[u] * L[u]);
}
int main()
{
    cin >> n >> m;
    for (int i = 1; i <= n; ++i)
    {
        int ytk;
        cin >> ytk >> v[i] >> L[i];
        add(ytk, i);
    }
    dfs(1);
    printf("%lld", ans);
    return 0;
}
