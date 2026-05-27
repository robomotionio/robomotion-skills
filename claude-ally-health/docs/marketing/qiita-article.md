# Claude Codeで構築するAIネイティブ個人健康管理システム

## はじめに

開発者として、自分の健康データを完全にコントロールしたいと思ったことはありませんか？

私は**Claude-Ally-Health**という、Claude Code CLIを使用したファイルベースの個人健康情報管理システムを開発しました。

## 特徴

### プライバシー優先
- 純粋なファイルベース存储、データベース不要
- クラウドアップロードなし、完全ローカル
- オープンソース（MITライセンス）

### AI機能
- 医療報告書の画像認識
- 薬物相互作用検出（5段階重症度システム）
- 13科のAI専門医による並列分析
- 放射線量追跡管理

### 技術スタック
- 存储: JSON + ファイルシステム
- CLI: Claude Code Slash Commands
- AI: マルチエージェントアーキテクチャ
- 画像認識: GLM 4.5V

## クイックスタート

```bash
git clone https://github.com/huifer/Claude-Ally-Health.git

# プロファイル設定
/profile set 175 70 1990-01-01

# 医療報告書を保存
/save-report /path/to/report.jpg

# 多専門家診察を開始
/consult
```

## アーキテクチャ

```
my-his/
├── .claude/
│   ├── commands/      # CLIコマンド定義
│   └── specialists/   # AI専門家スキル
├── data/
│   ├── profile.json
│   ├── medications/
│   ├── 生化检查/
│   └── interactions/
```

## 使い方の例

### 医療報告書を保存

```bash
/save-report @blood-test.jpg
```

→ 自動で値と基準値範囲を抽出
→ 異常値をフラグ
→ JSONとして保存

### 薬物相互作用をチェック

```bash
/interaction check
```

→ 現在の薬剤を分析
→ 相互作用を検出
→ 重症度（A/B/C/D/X）で警告

### 多専門家診察

```bash
/consult
```

→ 13科のAI専門家が並列分析
→ 総合的な推奨事項を生成

## 今後の展望

- [ ] 多言語対応（日本語、中国語、ドイツ語）
- [ ] Webダッシュボード
- [ ] モバイルアプリ
- [ ] EHRエクスポート形式

## リンク

- GitHub: https://github.com/huifer/Claude-Ally-Health
- ドキュメント: https://github.com/huifer/Claude-Ally-Health#readめ
- ライセンス: MIT

フィードバックをお待ちしています！

---

## 免責事項

このシステムは個人の健康管理を目的としており、医師の診断を代替するものではありません。
