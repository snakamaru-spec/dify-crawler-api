import json

class Code:
  def main(self, input_json: list) -> dict:
    # ツールからの出力はリスト形式で来ることがあるため、最初の要素を取得
    data = input_json[0] if input_json else {}
    
    # 辞書データから各値を取り出す
    page_count = data.get('page_count', 0)
    image_count = data.get('image_count', 0)

    # 次のLLMノードで使えるように、個別の変数として返す
    return {
      "page_count": page_count,
      "image_count": image_count
    }