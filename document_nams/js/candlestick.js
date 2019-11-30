  // ローソクチャートを表示する関数
  // candletypeには 1min 5min 1dayが選べる
function displayCandlestick(data, candleType, trades) {

    // グラフを挿入するエリア（card）のwidthを取得,（今回、heightはwidthの8/5に設定）
    let cardWidth = $(`.candlestick-${candleType}`).width();
    let cardHeight = cardWidth / 3;

    // グラフの領域とマージンを設定
    let margin = {top: 5, right: 5, bottom: 30, left: 80};
    let width = cardWidth - margin.left - margin.right;
    let height = cardHeight - margin.top - margin.bottom;

    // %Y-%m-%d %H:%M の形式のデータを受け取りパースするための変数
    let parseDate = d3.timeParse("%Y-%m-%d");

    // グラフ領域のうちx軸が占めるwidthを設定(今回は0~width)
    let x = techan.scale.financetime()
            .range([0, width]);

    // グラフ領域のうちy軸が占めるheightを設定
    // レートと出来高を7対3の比率に設定
    let y = d3.scaleLinear()
            .range([height * 7 / 10, 0]);
    let yVolume = d3.scaleLinear()
            .range([height, height * 7 / 10]);

    // ローソク足チャートをcandlestickとして定義
    let candlestick = techan.plot.candlestick()
            .xScale(x)
            .yScale(y);

    // x軸の定義
    var xAxis = d3.axisBottom()
        .scale(x)
        .tickFormat(d3.timeFormat("%m/%d")) // 日足なので、月(略称)表示にする
        .ticks(width/90); // 何データずつメモリ表示するか(レスポンシブ対応するためwidthによって変わるようにする)

    // y軸(レート)の定義
    let yAxis = d3.axisLeft()
            .scale(y)
            .ticks(height/70); // 何データずつメモリ表示するか

    // 移動平均線をsmaとして定義(単純移動平均線 SMA: Simple Moving Average)
    let sma = techan.plot.sma()
            .xScale(x)
            .yScale(y);

    // y軸(出来高)の定義
    let volume = techan.plot.volume()
            .xScale(x)
            .yScale(yVolume);

    // 線
    let close = techan.plot.close()
            .xScale(x)
            .yScale(y);

    // svgの挿入（既存のチャートを削除してから挿入）
    $(`.candlestick-${candleType}`).children("svg").remove();
    let svg = d3.select(`.candlestick-${candleType}`)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // 日時で並べ替えを行う
    let cAccessor = candlestick.accessor();
    let vAccessor = volume.accessor();
    // 最大180個のデータ数を表示する
    max_length = 180
    if (data.length > max_length) {
      var first_data = data.length - max_length;
    } else {
      var first_data = 0;
    }
    data = data.slice(first_data, data.length).map(function(d) {
      return {
          date: parseDate(d.Date),
          open: +d.Open,
          high: +d.High,
          low: +d.Low,
          close: +d.Close,
          volume: +d.Volume
      };
    }).sort(function(a, b) { return d3.ascending(cAccessor.d(a), cAccessor.d(b)); });
    // 描画関数
    x.domain(data.map(cAccessor.d));
    y.domain(techan.scale.plot.ohlc(data, cAccessor).domain());
    yVolume.domain(techan.scale.plot.volume(data, vAccessor.v).domain());

    // 出来高を挿入する
    svg.append("g")
            .attr("class", "volume")
            .data([data])
            .call(volume);
    // ローソク足を挿入する
    svg.append("g")
            .attr("class", "candlestick")
            .data([data])
            .call(candlestick);
    // 移動平均線（データ数25）を追加する
    svg.append("g")
            .attr("class", "sma ma5")
            .datum(techan.indicator.sma().period(5)(data))
            .call(sma);
    svg.append("g")
            .attr("class", "sma ma25")
            .datum(techan.indicator.sma().period(25)(data))
            .call(sma);
    svg.append("g")
            .attr("class", "sma close")
            .datum(data)
            .call(close);
    // x軸を追加する
    svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);
    // y軸（出来高）を追加する
    svg.append("g")
            .call(d3.axisLeft(yVolume)
            .ticks(height/150) // 何データずつメモリ表示するか
            .tickFormat(d3.format(",.3s")));
    // y軸（レート）を追加する
    svg.append("g")
            .attr("class", "y axis")
            .call(yAxis);
    // y軸のラベルを追加する
    svg.append("g")
            .append("text")
            .attr("transform", "rotate(-90)") // Y軸ラベルを縦書きに
            .attr("y", 15) // 位置調整
            .style("text-anchor", "end") // テキスト開始位置
            .text("価格 (円)");

    // ==============================
    // trade arrow
    // ==============================
    if (trades.length != 0) {
        var tradearrow = techan.plot.tradearrow()
                .xScale(x)
                .yScale(y)
                .orient(function(d) { return d.type.startsWith("buy") ? "up" : "down"; })
                .on("mouseenter", enter)
                .on("mouseout", out);
        trades = trades.slice(0, trades.length).map(function(d) {
          return {
              date: parseDate(d.date),
              type: d.type,
              price: d.price,
              quantity: d.quantity
          };
        }).sort(function(a, b) { return d3.ascending(cAccessor.d(a), cAccessor.d(b)); });
        svg.append("g")
                    .attr("class", "tradearrow");
        svg.selectAll("g.tradearrow").datum(trades).call(tradearrow);
    }

    function enter(d) {
        valueText.style("display", "inline");
        refreshText(d);
    }

    function out() {
        valueText.style("display", "none");
    }
}

//---------------------------------------------------------------------------------------
// APIから情報を取得し、内部でdisplayCandlestickを呼び出す関数
// candleTypeには 1min 5min 1dayが選べる
function getAPIAndDisplayCandlestick(candleType, code, trades) {
    // コントローラーにリクエストを送る
    let requestUrl = "/api/stock_value_data/?stock="+code+"&limit=180";
    $.ajax({
      url: requestUrl,
      type: 'get',
      dataType: 'json',
      data: {
        candleType: candleType,
        trades: trades,
      }
    })
    .done(function(json) {
      // ローソク足チャートに必要な情報を取り出す
      let row_data = json.results
      // 配列dataに連想配列としてデータを入れる
      let data = [];
      row_data.forEach(function(datum) {
        let open = datum.val_open;
        let high = datum.val_high;
        let low = datum.val_low;
        let close = datum.val_close;
        let volume = datum.turnover;
        let date = datum.date;
        let modifiedDatum = { Date: date, Open: open, High: high, Low: low, Close: close, Volume: volume };
        data.push(modifiedDatum);
      })
      // 画面を読み込んだ時に発火する
      displayCandlestick(data, candleType, trades);
    })
    .fail(function() {
      alert('error');
    });
}

