# momo AI Auto Trader (Scaffold)

momo証券（moomoo OpenAPI）向けの自動売買システム雛形です。  
このリポジトリは **まずはローカルで安全に動く Paper Trading + ダッシュボード** を提供します。

## できること
- シンプルなAIモデルで「次の足が上がる確率」を推定
- しきい値に応じて自動売買（現状はPaper Broker）
- 約定履歴・資産推移をSQLiteに保存
- StreamlitダッシュボードでPC確認

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Windows (PowerShell) の場合
```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e '.[dev]'
```

> `pip install -e .[dev]` が PowerShell で止まる場合は、`[]` がワイルドカード扱いされている可能性があります。  
> その場合は必ず **`pip install -e '.[dev]'`** のようにクォートしてください。
>
> `Multiple top-level packages discovered in a flat-layout: ['app', 'data']` が出る場合は、
> 旧版の `pyproject.toml` を使っている可能性があります。最新コードを pull して再実行してください。

## 実行
1) ダミーデータで売買シグナルを実行（デフォルトで都度確認あり）
```bash
python run_trader.py
```

2) ダッシュボード起動
```bash
streamlit run dashboard.py
```

## 手動承認フロー
- `run_trader.py` は `require_manual_approval=True` で起動するため、
  実際の売買前にコンソールで `実行しますか？ [y/N]` の確認が出ます。
- `y` の場合のみ約定、`N` の場合は見送りになります。
- ダッシュボードの「承認待ち/承認済みシグナル」で、投資/売買理由と承認結果を確認できます。

## ファイル構成
- `app/model.py`: 特徴量 + 予測モデル
- `app/trader.py`: 売買判断と注文実行
- `app/broker.py`: PaperBroker / MoomooBroker(未実装)
- `app/db.py`: DBスキーマと保存処理
- `dashboard.py`: 履歴確認UI

## 本番化するときに必要な作業
- `MoomooBroker` へ実際のOpenAPI認証・発注を実装
- 銘柄/市場ごとの取引ルール（時間帯、最小数量、手数料）反映
- 最大損失・停止条件・再接続制御の強化
- バックテストとウォークフォワード評価

## 注意
本コードは教育・検証用です。投資判断は自己責任で行ってください。
