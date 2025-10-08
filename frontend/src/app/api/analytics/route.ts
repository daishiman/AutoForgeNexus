import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const data = await request.json();

  // ログ記録（本番では監視システムへ送信）
  // eslint-disable-next-line no-console
  console.log('Web Vitals:', data);

  // LangFuseや他の監視システムへ転送
  // await sendToLangFuse(data);

  return NextResponse.json({ success: true });
}
