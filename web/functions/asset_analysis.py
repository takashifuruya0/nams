from django_pandas.io import read_frame
import logging
logger = logging.getLogger('django')


def prepare(svds):
    df = read_frame(svds)
    # 終値前日比, 出来高前日比
    df['val_close_diff'] = -(df['val_close'].shift() - df['val_close'])
    df['val_close_diff_pct'] = round(
        -(df['val_close'].shift() - df['val_close']) / df['val_close'].shift() * 100, 1)
    df['turnover_diff'] = -(df['turnover'].shift() - df['turnover'])
    df['turnover_diff_pct'] = round(
        -(df['turnover'].shift() - df['turnover']) / df['turnover'].shift() * 100, 1)
    # 終値-始値
    df['val_close_open'] = df['val_close'] - df['val_open']
    # 陽線/陰線
    df['is_positive'] = False
    df['is_positive'] = df['is_positive'].where(df['val_close_open'] < 0, True)
    # 下ひげ/上ひげ
    df['lower_mustache'] = (df['val_open'] - df['val_low']).where(df['is_positive'], df['val_close'] - df['val_low'])
    df['upper_mustache'] = (df['val_high'] - df['val_close']).where(df['is_positive'], df['val_high'] - df['val_open'])
    # 移動平均
    df['ma_5'] = df.val_close.rolling(window=5, min_periods=1).mean()
    df['ma_25'] = df.val_close.rolling(window=25, min_periods=1).mean()
    df['ma_75'] = df.val_close.rolling(window=75, min_periods=1).mean()
    df['ma_diff5_25'] = df.ma_5 - df.ma_25
    df['ma_diff5_25_pct'] = df.ma_diff5_25 / df.ma_75
    df['ma_diff25_75'] = df.ma_25 - df.ma_75
    df['ma_diff25_75_pct'] = df.ma_diff25_75 / df.ma_75
    # ボリンジャーバンド（25日）
    df["sigma_25"] = df.val_close.rolling(window=25).std()
    df["ma_25p2sigma"] = df.ma_25 + 2 * df.sigma_25
    df["ma_25m2sigma"] = df.ma_25 - 2 * df.sigma_25
    # return
    return df


def get_trend(df):
    try:
        df_reverse = df.sort_values('date', ascending=False)
        ma_25 = df_reverse['ma_25']
        ma_75 = df_reverse['ma_75']
        res = dict()
        trend_period_25 = 1
        trend_period_75 = 1
        # 25
        if ma_25.iloc[0] > ma_25.iloc[1]:
            res['is_upper_25'] = True
            for i in range(2, len(df_reverse)):
                if ma_25.iloc[i-1] > ma_25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break
        elif ma_25.iloc[0] < ma_25.iloc[1]:
            res['is_upper_25'] = False
            for i in range(2, len(df_reverse)):
                if ma_25.iloc[i-1] < ma_25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break
        # 75
        if ma_75.iloc[0] > ma_75.iloc[1]:
            res['is_upper_75'] = True
            for i in range(2, len(df_reverse)):
                if ma_75.iloc[i-1] > ma_75.iloc[i]:
                    trend_period_75 += 1
                else:
                    break
        elif ma_75.iloc[0] < ma_75.iloc[1]:
            res['is_upper_75'] = False
            for i in range(2, len(df_reverse)):
                if ma_75.iloc[i-1] < ma_75.iloc[i]:
                    trend_period_75 += 1
                else:
                    break
        # res
        res['period_25'] = trend_period_25
        res['period_75'] = trend_period_75

    except Exception as e:
        logger.error("get_trend was failed")
        logger.error(e)
        res = {
            "is_upper_25": None,
            "period_25": None,
            "is_upper_75": None,
            "period_75": None,
        }
    finally:
        return res


def check(df):
    trend = get_trend(df)
    df_reverse = df.sort_values('date', ascending=False)
    data = {key: list() for key in (
        "たくり線_底", "包線_天井", "包線_底", "はらみ線_底", "上げ三法_底", "三手大陰線_底"
    )}
    for i in range(len(df_reverse)-1):
        # 陽線・陰線の長さ
        bar1 = abs(df_reverse.iloc[i+1]['val_close_open'])
        bar0 = abs(df_reverse.iloc[i]['val_close_open'])
        # たくり線
        if df_reverse.iloc[i]['lower_mustache'] > 2 * df_reverse.iloc[i]['upper_mustache'] \
                and not trend['is_upper_25'] and trend['period_25'] > 2:
            msg = "たくり線：底" \
                  + "（ヒゲ：" + str(df_reverse.iloc[i]['lower_mustache']) \
                  + " / 線：" + str(abs(df_reverse.iloc[i]['val_close_open'])) \
                  + "）"
            data["たくり線_底"].append(df_reverse.iloc[i])
            logger.info("{}: {}".format(df_reverse.iloc[i]['date'], msg))
        # 包線
        if not df_reverse.iloc[i+1]['is_positive'] and df_reverse.iloc[i]['is_positive'] \
                and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_open'] \
                and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_close']:
            # 陰線→陽線
            if trend['is_upper_25'] and trend['period_25'] > 2:
                # 上昇傾向→天井
                msg = "包み陽線：天井（" + str(bar1) + "→" + str(bar0) + "）"
                logger.info(msg)
                data['包線_天井'].append(df_reverse.iloc[i])
            elif not trend['is_upper_25'] and trend['period_25'] > 2:
                # 下落傾向→底
                msg = "包み陽線：底（" + str(bar1) + "→" + str(bar0) + "）"
                logger.info(msg)
                data['包線_底'].append(df_reverse.iloc[i])
            else:
                # 傾向なし
                pass
        elif df_reverse.iloc[i+1]['is_positive'] and not df_reverse.iloc[i]['is_positive'] \
                and df_reverse.iloc[i+1]['val_close'] < df_reverse.iloc[i]['val_open'] \
                and df_reverse.iloc[i+1]['val_open'] > df_reverse.iloc[i]['val_close']:
            # 陽線→陰線
            if trend['is_upper_25'] and trend['period_25'] > 2:
                # 上昇傾向→天井
                msg = "包み陰線：天井（" + str(bar1) + "→" + str(bar0) + "）"
                logger.info(msg)
                data['包線_天井'].append(df_reverse.iloc[i])
            elif not trend['is_upper_25'] and trend['period_25'] > 2:
                # 下落傾向→底
                msg = "包み陰線：底（" + str(bar1) + "→" + str(bar0) + "）"
                logger.info(msg)
                data['包線_底'].append(df_reverse.iloc[i])
            else:
                # 傾向なし
                pass
        else:
            pass

        # 2. はらみ線
        if not df_reverse.iloc[1]['is_positive'] \
                and df_reverse.iloc[0]['is_positive'] \
                and df_reverse.iloc[1]['val_end'] < df_reverse.iloc[0]['val_open'] \
                and df_reverse.iloc[1]['val_open'] > df_reverse.iloc[0]['val_end'] \
                and trend['is_upper_25'] and trend['period_25'] > 2:
            # 陰の陽はらみ
            msg = "陰の陽はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            data['はらみ線_底'].append(df_reverse.iloc[i])
            logger.info(msg)
        elif not df_reverse.iloc[1]['is_positive'] \
                and not df_reverse.iloc[0]['is_positive'] \
                and df_reverse.iloc[1]['val_open'] < df_reverse.iloc[0]['val_open'] \
                and df_reverse.iloc[1]['val_close'] > df_reverse.iloc[0]['val_close'] \
                and trend['is_upper_25'] and trend['period_25'] > 2:
            # 陰の陰はらみ
            msg = "陰の陰はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            data['はらみ線_底'].append(df_reverse.iloc[i])
            logger.info(msg)
        elif df_reverse.iloc[1]['is_positive'] \
                and df_reverse.iloc[0]['is_positive'] \
                and df_reverse.iloc[1]['val_open'] < df_reverse.iloc[0]['val_open'] \
                and df_reverse.iloc[1]['val_close'] > df_reverse.iloc[0]['val_close'] \
                and not trend['is_upper_25'] and trend['period_25'] > 2:
            # 陽の陽はらみ
            msg = "陽の陽はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            data['はらみ線_底'].append(df_reverse.iloc[i])
            logger.info(msg)
        elif df_reverse.iloc[1]['is_positive'] \
                and not df_reverse.iloc[0]['is_positive'] \
                and df_reverse.iloc[1]['val_open'] < df_reverse.iloc[0]['val_close'] \
                and df_reverse.iloc[1]['val_close'] > df_reverse.iloc[0]['val_open'] \
                and not trend['is_upper_25'] and trend['period_25'] > 2:
            # 陽の陰はらみ
            msg = "陰の陰はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            data['はらみ線_底'].append(df_reverse.iloc[i])
            logger.info(msg)
        else:
            pass

        # 3. 上げ三法: 1本目の安値を割り込まない, 4本目が1本目の終値を超える
        if not df_reverse.iloc[3]['is_positive'] and not df_reverse.iloc[2]['is_positive'] \
                and not df_reverse.iloc[1]['is_positive'] and df_reverse.iloc[0]['is_positive'] \
                and df_reverse.iloc[3]['val_open'] > df_reverse.iloc[2]['val_open'] \
                and df_reverse.iloc[3]['val_open'] > df_reverse.iloc[1]['val_open'] \
                and df_reverse.iloc[1]['val_close'] < df_reverse.iloc[0]['val_open'] \
                and df_reverse.iloc[3]['val_open'] < df_reverse.iloc[0]['val_close']:
            logger.info("上げ三法：◯")
            data['上げ三法_底'].append(df_reverse.iloc[i])
        else:
            pass

        # 4. 三空叩き込み
        if not df_reverse.iloc[3]['is_positive'] and not df_reverse.iloc[2]['is_positive'] \
                and not df_reverse.iloc[1]['is_positive'] and not df_reverse.iloc[0][
            'is_positive'] \
                and df_reverse.iloc[3]['val_open'] < df_reverse.iloc[2]['val_close'] \
                and df_reverse.iloc[2]['val_open'] < df_reverse.iloc[1]['val_close'] \
                and df_reverse.iloc[1]['val_open'] < df_reverse.iloc[0]['val_close']:
            logger.info("三空叩き込み：◯")
            data['三空叩き込み_底'].append(df_reverse.iloc[i])
        else:
            pass

        # 5. 三手大陰線
        if not df_reverse.iloc[2]['is_positive'] and not df_reverse.iloc[1][
            'is_positive'] and not df_reverse.iloc[0]['is_positive'] \
                and -df_reverse.iloc[2]['val_close-start'] / df_reverse.iloc[2]['val_close'] > 0.05 \
                and -df_reverse.iloc[1]['val_close-start'] / df_reverse.iloc[1]['val_close'] > 0.05 \
                and -df_reverse.iloc[0]['val_close-start'] / df_reverse.iloc[0]['val_close'] > 0.05:
            logger.info("三手大陰線：◯")
            data['三手大陰線_底'].append(df_reverse.iloc[i])
        else:
            pass
    return data
