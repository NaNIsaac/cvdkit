# cvdkit

[English](README.md) | [한국어](README.ko.md)

matplotlib용 색각 이상 안전 스타일입니다. 적색약(protan)·녹색약(deutan)·청색약(tritan) 시뮬레이션에서도
서로 구별되는 팔레트, 색과 함께 바뀌는 마커·점선 패턴·해칭, 그리고 그림에서 색으로만 구별되는 계열을
찾아내는 검사를 제공합니다.

## 설치

Python 3.12 이상이 필요합니다. PyPI에 첫 릴리스가 올라가기 전까지는 이 저장소를 clone한 폴더에서
설치합니다.

<!-- test unix -->
```sh
uv venv
uv pip install .
```

<!-- test windows -->
```powershell
uv venv
uv pip install .
```

import되는지 확인합니다.

<!-- test unix -->
```sh
uv run --no-project python -c "import cvdkit; print(cvdkit.pick(3).colors)"
```

<!-- test windows -->
```powershell
uv run --no-project python -c "import cvdkit; print(cvdkit.pick(3).colors)"
```

## 사용법

```python
import matplotlib.pyplot as plt
import cvdkit

p = cvdkit.pick(4)  # 모든 시뮬레이션에서 구별되는 4색
fig, ax = plt.subplots()
ax.set_prop_cycle(p.cycler())  # 색, 마커, 점선 패턴이 함께 바뀜
for k in range(4):
    ax.plot(range(10), [k * x for x in range(10)], label=f"k={k}")
ax.legend()

for c in cvdkit.check(fig):  # 색으로만 구별되는데 색이 겹치는 쌍
    print(c.a, c.b, c.view, c.color_a, c.color_b)

sim = cvdkit.simulate(fig, "deutan")  # 녹색맹으로 본 그림의 RGB 배열
plt.imsave("figure_deutan.png", sim)
```

- `simulate(obj, kind, severity)`는 figure, 이미지 배열, 색 지정을 받습니다. `kind`는 `"protan"`,
  `"deutan"`, `"tritan"`이고 `severity`는 0에서 1까지이며 1이 2색형 색각입니다.
- `check(fig)`는 각 Axes 안의 선, scatter 묶음, 막대 묶음을 비교합니다. 색 말고는 구별할 것이 없고(마커,
  점선 패턴, 해칭이 같고) 시뮬레이션 하나에서라도 색이 겹치면 그 쌍을 보고합니다. 컬러맵 이미지는 검사하지
  않으므로 `simulate`로 직접 봅니다.
- `distinguishable(a, b)`와 `separation(a, b, view)`는 두 색에 같은 기준을 적용합니다.
- `pick(n, background)`는 팔레트(기본 Okabe-Ito)에서 모든 시뮬레이션에서 가장 가까운 쌍이 가장 먼 `n`색을
  고르고, 배경에 묻히는 색은 뺍니다. 팔레트가 구별할 수 있는 수를 넘으면 색은 반복되고 마커, 점선, 해칭이
  계열을 구별합니다.
- `style_cycler(colors)`와 `hatch_cycler(colors)`는 아무 색 목록으로 cycler를 만듭니다.
- `palette(name)`과 `colormap(name)`은 아래 데이터를 줍니다.

### 두 색을 구별된다고 보는 기준

선과 마커는 정상 색각과 각 시뮬레이션 모두에서 CIELAB 명도 차가 10 이상이거나, 두 색 모두 채도 15 이상이면서
색상각 차가 30도 이상이어야 합니다. 면은 CIEDE2000 차가 10 이상이면 됩니다. 선에서는 채도 차만으로는 구별된다고
보지 않습니다. `#eb6834`와 `#1baf7a`는 녹색맹 시뮬레이션에서 CIEDE2000 거리가 약 17로 아래 팔레트의 일부
쌍보다 크지만, 둘 다 같은 명도의 중간 올리브색이 되어 가는 선에서는 어느 쪽인지 알 수 없습니다. 이 기준값은 이
패키지에서 정한 작업값이며 연구에서 나온 값이 아닙니다.

## 데이터

[docs/swatches.png](docs/swatches.png)는 모든 팔레트를 원래 색 그대로, 마커와 점선이 있는 선과 해칭 막대로
보여줍니다(`examples/swatches.py`로 그림).

범주형 팔레트와, 정상 색각 및 severity 1 시뮬레이션에서의 최소 쌍별 CIEDE2000입니다.

| 이름 | 색 수 | 정상 | protan | deutan | tritan | 출처 | 조건 |
|---|---|---|---|---|---|---|---|
| `okabe_ito` | 8 | 21.7 | 12.2 | 11.6 | 10.9 | Okabe and Ito; Wong 2011 | 출처 표기 시 자유 사용 |
| `tol_bright` | 7 | 20.5 | 14.2 | 14.8 | 8.6 | Tol | BSD-3-Clause |
| `tol_vibrant` | 7 | 18.3 | 13.7 | 14.4 | 8.6 | Tol | BSD-3-Clause |
| `tol_muted` | 9 | 15.0 | 11.8 | 14.3 | 11.5 | Tol | BSD-3-Clause |
| `tol_high_contrast` | 3 | 38.9 | 26.0 | 25.3 | 21.2 | Tol | BSD-3-Clause |
| `petroff6` | 6 | 17.9 | 10.6 | 14.7 | 18.3 | Petroff 2021 | CC0-1.0 |
| `petroff8` | 8 | 20.0 | 9.0 | 14.5 | 11.7 | Petroff 2021 | CC0-1.0 |
| `petroff10` | 10 | 17.3 | 11.9 | 12.6 | 13.3 | Petroff 2021 | CC0-1.0 |

컬러맵: `colormap("tol_sunset")`과 `colormap("tol_BuRd")`는 Tol의 발산형 컬러맵입니다. 순차형 데이터에는
matplotlib의 `cividis`(Nuñez et al. 2018)나 `viridis`를 쓰고, Crameri의 과학용 컬러맵(Crameri et al. 2020)은
`cmcrameri` 패키지에 있습니다.

Tol 색은 `tol_colors` 패키지에서 가져왔고 BSD-3-Clause 고지는
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)에 있습니다.

## 참고문헌

참고문헌 목록은 [README.md](README.md#references)에 있습니다.

## 라이선스

MIT. 팔레트 데이터는 위에 적은 조건을 따릅니다.
