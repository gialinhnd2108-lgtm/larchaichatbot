import streamlit as st
import google.generativeai as genai

# Tự động lấy API Key từ kho bảo mật Secrets
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["AQ.Ab8RN6ISVghj6Xox2I70PmMRp9G6wE0_6lrvraEkYDzdGBwn6Q"]
    genai.configure(api_key=api_key)
else:
    st.error("Chưa cấu hình GOOGLE_API_KEY trong Secrets!")
    st.stop()
# ==========================================
# 1. CẤU HÌNH TRANG & TỪ ĐIỂN SONG NGỮ (i18n)
# ==========================================
st.set_page_config(page_title="Người Bạn AI Đồng Hành", page_icon="🌱", layout="wide")

if 'lang' not in st.session_state:
    st.session_state.lang = 'vi'

def switch_lang(lang):
    st.session_state.lang = lang

translations = {
    'vi': {
        'title': "🌱 Trợ Lý Tâm Lý Học Đường",
        'subtitle': "Cầu nối thấu cảm giữa học sinh và gia đình.",
        'sidebar_title': "⚙️ Cài đặt",
        'api_key_prompt': "Nhập Google Gemini API Key:",
        'role_select': "Bạn đang truy cập với tư cách là:",
        'roles': ['🎓 Học sinh', '👨‍👩‍👧 Phụ huynh'],
        'chat_placeholder_student': "Cậu đang nghĩ gì thế? Chia sẻ với mình nhé...",
        'chat_placeholder_parent': "Anh/chị đang trăn trở điều gì về con? Hãy chia sẻ nhé...",
        'suggest_title': "💡 Gợi ý chủ đề trò chuyện:",
        
        # Danh mục cho Học sinh
        'cat_student': {
            'Học tập': '📚 Học tập',
            'Gia đình': '🏠 Gia đình',
            'Tình cảm': '❤️ Tình cảm',
            'Định hướng': '🧭 Định hướng',
            'Cảm xúc': '🌪️ Cảm xúc'
        },
        # Danh mục cho Phụ huynh
        'cat_parent': {
            'Tâm lý': '🧠 Tâm lý tuổi teen',
            'Hành vi': '⚠️ Giải mã hành vi',
            'Thấu hiểu': '🤝 Cách thấu hiểu con',
            'Hành động': '🛠️ Cần làm gì?'
        },
        
        'sys_student': """Bạn là một người bạn 16-18 tuổi, vô cùng thấu cảm và hiểu tâm lý học sinh THPT. 
- Xưng hô "mình - bạn" hoặc "tớ - cậu". 
- Luôn LẮNG NGHE, CÔNG NHẬN cảm xúc trước tiên. Không phán xét.
- Trả lời ngắn gọn, chân thành, tự nhiên như tin nhắn bạn bè, gợi mở bằng câu hỏi nhẹ nhàng.""",
        
        'sys_parent': """Bạn là một chuyên gia tâm lý học đường thấu cảm, chuyên hỗ trợ phụ huynh thấu hiểu con cái tuổi vị thành niên (16-18 tuổi).
- Xưng hô "tôi" và "anh/chị". Vibe điềm tĩnh, ấm áp, không phán xét cha mẹ.
- Khi phụ huynh lo lắng về hành vi tiêu cực hoặc nổi loạn của con, hãy an ủi họ trước, sau đó nhẹ nhàng giải mã tâm lý ẩn sau hành vi đó của trẻ.
- Đưa ra lời khuyên thực tế, hướng dẫn cách giao tiếp không bạo lực và cách đặt câu hỏi gợi mở với con."""
    },
    'en': {
        'title': "🌱 School Psychology Assistant",
        'subtitle': "An empathetic bridge between students and families.",
        'sidebar_title': "⚙️ Settings",
        'api_key_prompt': "Enter Google Gemini API Key:",
        'role_select': "You are accessing as:",
        'roles': ['🎓 Student', '👨‍👩‍👧 Parent'],
        'chat_placeholder_student': "What's on your mind? Share it with me...",
        'chat_placeholder_parent': "What are your concerns about your child? Share them here...",
        'suggest_title': "💡 Suggested Topics:",
        
        'cat_student': {'Học tập': '📚 Study', 'Gia đình': '🏠 Family', 'Tình cảm': '❤️ Love', 'Định hướng': '🧭 Future', 'Cảm xúc': '🌪️ Emotions'},
        'cat_parent': {'Tâm lý': '🧠 Teen Psychology', 'Hành vi': '⚠️ Behavior Decoding', 'Thấu hiểu': '🤝 Understanding', 'Hành động': '🛠️ Action Plan'},
        
        'sys_student': """You are an empathetic 16-18 year old peer. 
- Always validate feelings first. Be warm and non-judgmental.
- Keep responses concise, natural, and text-like. Use gentle open-ended questions.""",
        
        'sys_parent': """You are an empathetic school psychologist helping parents understand their teens.
- Tone: Calm, warm, non-judgmental towards the parents.
- Validate the parents' worries first, then gently decode the hidden psychology behind the teen's behavior.
- Give actionable, practical advice on non-violent communication."""
    }
}

t = translations[st.session_state.lang]

# ==========================================
# 2. BỘ CÂU HỎI GỢI Ý ĐỘNG TỪ ẢNH
# ==========================================
suggested_questions = {
    'vi': {
        'Học sinh': {
            'Học tập': ["Làm sao để ghi nhớ các công thức Toán/Lý/Hóa phức tạp mà không cần học vẹt?", "Mình bị xao nhãng bởi điện thoại mỗi khi ngồi vào bàn học, có cách nào khắc phục không?"],
            'Gia đình': ["Bố mẹ lúc nào cũng so sánh mình với mấy bạn giỏi, mình nên mở lời thế nào?", "Bố mẹ hay soi xét quyền riêng tư như đọc tin nhắn, làm sao để thiết lập ranh giới?"],
            'Tình cảm': ["Cảm giác yêu đơn phương một người tốn năng lượng quá, làm sao để buông bỏ?", "Mình bị bạn bè trong lớp hiểu lầm và cô lập, làm sao vượt qua?"],
            'Định hướng': ["Bố mẹ muốn mình chọn ngành an toàn, nhưng mình lại muốn mạo hiểm theo đam mê...", "Sự phát triển của AI có khiến ngành mình dự định học bị biến mất không?"],
            'Cảm xúc': ["Cảm giác trống rỗng, không vui cũng chẳng buồn kéo dài nhiều ngày liền là sao vậy?", "Tại sao mình lại hay có xu hướng ăn rất nhiều hoặc bỏ bữa hoàn toàn khi bị stress?"]
        },
        'Phụ huynh': {
            'Tâm lý': [
                "Tại sao con ở độ tuổi này lại trở nên khép kín, ít chia sẻ và hay giận dỗi với cha mẹ?", 
                "Nỗi sợ thất bại và sợ làm cha mẹ thất vọng ảnh hưởng thế nào đến tâm lý thi cử của con?",
                "Khủng hoảng bản sắc tuổi 18 ảnh hưởng thế nào đến cách con lựa chọn tương lai?"
            ],
            'Hành vi': [
                "Con thức rất khuya xem điện thoại, điểm số sa sút đột ngột là dấu hiệu của vấn đề tâm lý nào?",
                "Việc con bắt đầu có thái độ hỗn xược và thách thức 'bố mẹ đánh con đi' thể hiện tâm lý bất cần nào?",
                "Việc con tự cô lập bản thân, bỏ ăn hoặc có dấu hiệu tự làm đau mình có ý nghĩa gì?"
            ],
            'Thấu hiểu': [
                "Làm thế nào để mở lời trò chuyện với con khi con luôn tỏ ra chống đối và thu mình lại?",
                "Làm sao để nhận biết con đang gặp áp lực nặng nề ở trường mà con không chịu nói ra?",
                "Đặt câu hỏi như thế nào để con cảm thấy an toàn, không bị phán xét và chịu chia sẻ?"
            ],
            'Hành động': [
                "Tôi nên làm gì ngay khi phát hiện con có dấu hiệu bị căng thẳng kịch liệt, lo âu hoặc trầm cảm?",
                "Nên phản ứng thế nào khi con công khai thiên hướng tình dục với gia đình?",
                "Khi thấy con bị xao nhãng học hành vì chuyện tình cảm tuổi học trò, cha mẹ nên xử lý thế nào cho khéo?"
            ]
        }
    },
    'en': {
        'Học sinh': {
            'Học tập': ["How to memorize complex Math/Physics formulas without rote learning?", "I get distracted by my phone, how to fix this?"],
            'Gia đình': ["Parents always compare me to others, how to talk to them?", "How to set boundaries when parents invade my privacy?"],
            'Tình cảm': ["Unrequited love is draining me, how to let go?", "I'm isolated by classmates, how to survive this?"],
            'Định hướng': ["Parents want a safe major, but I want to follow my passion...", "Will AI replace my future career?"],
            'Cảm xúc': ["Feeling empty, neither happy nor sad for days, what's wrong?", "Why do I binge eat or starve when stressed?"]
        },
        'Phụ huynh': {
            'Tâm lý': ["Why is my teen becoming withdrawn and easily irritated?", "How does the fear of disappointing parents affect their exam psychology?", "How does an identity crisis affect their future choices?"],
            'Hành vi': ["Staying up late on the phone and grades dropping—what does this mean?", "What psychology is behind a rebellious 'go ahead and hit me' attitude?", "What does it mean if my child isolates themselves or shows signs of self-harm?"],
            'Thấu hiểu': ["How to start a conversation when they are constantly defensive?", "How to tell if my child is under severe school pressure if they won't speak?", "How to ask questions so they feel safe to share?"],
            'Hành động': ["What should I do immediately if my child shows signs of severe anxiety/depression?", "How to react if my child comes out to the family?", "How to handle it if puppy love is distracting them from studies?"]
        }
    }
}

# ==========================================
# 3. GIAO DIỆN CHÍNH & SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown(f"### {t['sidebar_title']}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇻🇳 Tiếng Việt", use_container_width=True): switch_lang('vi')
    with col2:
        if st.button("🇬🇧 English", use_container_width=True): switch_lang('en')
    
    st.divider()
    api_key = st.text_input(t['api_key_prompt'], type="password")
    if not api_key:
        st.warning("⚠️ Vui lòng nhập API Key!")

st.title(t['title'])
st.markdown(f"*{t['subtitle']}*")

# CHỌN VAI TRÒ
user_role = st.radio(t['role_select'], t['roles'], horizontal=True)
is_student = "Học sinh" in user_role or "Student" in user_role
current_role_key = 'Học sinh' if is_student else 'Phụ huynh'

# ==========================================
# 4. LỊCH SỬ CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_lang" not in st.session_state:
    st.session_state.current_lang = st.session_state.lang
if "current_role" not in st.session_state:
    st.session_state.current_role = current_role_key

# Xóa chat nếu đổi ngôn ngữ hoặc đổi vai trò (tránh AI bị lú)
if st.session_state.current_lang != st.session_state.lang or st.session_state.current_role != current_role_key:
    st.session_state.messages = []
    st.session_state.current_lang = st.session_state.lang
    st.session_state.current_role = current_role_key

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. KHU VỰC GỢI Ý THEO VAI TRÒ
# ==========================================
st.markdown(f"#### {t['suggest_title']}")
active_categories = t['cat_student'] if is_student else t['cat_parent']
tabs = st.tabs(list(active_categories.values()))
active_qs = suggested_questions[st.session_state.lang][current_role_key]

selected_prompt = None
for i, (cat_key, qs) in enumerate(active_qs.items()):
    with tabs[i]:
        for q in qs:
            if st.button(q, key=q):
                selected_prompt = q

# ==========================================
# 6. XỬ LÝ LOGIC TRÒ CHUYỆN
# ==========================================
placeholder_text = t['chat_placeholder_student'] if is_student else t['chat_placeholder_parent']
user_input = st.chat_input(placeholder_text)
prompt = user_input or selected_prompt

if prompt:
    if not api_key:
        st.error("Khoan đã! Bạn chưa nhập API Key ở menu bên trái kìa.")
    else:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        genai.configure(api_key=api_key)
        
        # Chọn System Prompt dựa trên vai trò
        system_prompt = t['sys_student'] if is_student else t['sys_parent']
        
        full_prompt = f"{system_prompt}\n\nLịch sử trò chuyện:\n"
        for msg in st.session_state.messages[:-1]:
            sender = "Người dùng" if msg['role'] == "user" else "Bạn"
            full_prompt += f"{sender}: {msg['content']}\n"
        full_prompt += f"\nNgười dùng: {prompt}\nPhản hồi của bạn:"

        model = genai.GenerativeModel('gemini-1.5-flash')

        try:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                response = model.generate_content(full_prompt)
                message_placeholder.markdown(response.text)
                
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Lỗi rồi: {e}")
# ==========================================
# 2. BỘ CÂU HỎI GỢI Ý (FULL 100% SONG NGỮ VIỆT - ANH)
# ==========================================
suggested_questions = {
    'vi': {
        'Học sinh': {
            'Học tập': [
                "Chỉ còn ít thời gian nữa là thi rồi mà mình thấy kiến thức vẫn trống rỗng, mình nên bắt đầu từ đâu?",
                "Mình rất dễ bị xao nhãng bởi điện thoại mỗi khi ngồi vào bàn học, có cách nào khắc phục không?",
                "Học trước quên sau, dạo này đầu óc mình trì trệ lắm, làm sao để tăng khả năng ghi nhớ?",
                "Làm sao để vượt qua cảm giác kiệt sức khi phải học liên tục ngày đêm?",
                "Mình bị mất gốc môn học ..., bây giờ chạy đà năm lớp 12 liệu có còn kịp không?",
                "Phương pháp học Pomodoro hay Active Recall có thực sự hiệu quả cho việc ôn thi tốt nghiệp không?",
                "Làm sao để duy trì sự tập trung khi tự học ở nhà mà không bị cám dỗ bởi giường ngủ?",
                "Lịch học thêm dày đặc làm mình không có thời gian tự học, mình nên sắp xếp lại thế nào?",
                "Càng sát ngày thi mình càng thấy mình quên hết sạch kiến thức, đây có phải hiện tượng bình thường không?",
                "Làm sao để vượt qua cảm giác chán nản khi điểm thi thử lần này còn thấp hơn cả lần trước?",
                "Mình không thể nào nuốt nổi các môn học thuộc lòng như Sử/Địa/GDCD, có tips nào học nhanh không?",
                "Cảm giác học hoài không tiến bộ khiến mình muốn buông xuôi, làm sao để lấy lại động lực?",
                "Nên ưu tiên luyện đề hay học lại lý thuyết căn bản trong giai đoạn nước rút?",
                "Làm sao để phân bổ thời gian hợp lý giữa các môn thi tổ hợp và môn điều kiện?",
                "Việc thức khuya học bài đến 2-3h sáng có thực sự mang lại hiệu quả tốt hơn dậy sớm?",
                "Có nên sử dụng các loại thuốc bổ não hay thực phẩm chức năng để tăng cường trí nhớ không?",
                "Làm sao để chấm dứt tình trạng 'nước đến chân mới nhảy' trong việc làm bài tập/ôn thi?",
                "Môi trường học tập quá ồn ào tại nhà làm mình không thể tập trung, có giải pháp nào thay thế?",
                "Làm sao để giữ cho mắt không bị mỏi và đầu óc không bị đơ khi học liên tục nhiều tiếng?",
                "Có nên lập nhóm học tập chung với bạn bè hay tự học một mình sẽ hiệu quả hơn?",
                "Làm sao để ghi nhớ các công thức Toán/Lý/Hóa phức tạp mà không cần học vẹt?",
                "Có nên bỏ bớt một vài môn học không nằm trong khối thi đại học để dồn sức không?",
                "Khi cảm thấy quá tải kiến thức, mình nên nghỉ ngơi hoàn toàn bao lâu để hồi phục?",
                "Làm sao để tạo cảm hứng học tập đối với những môn học mình cực kỳ ghét?",
                "Có nên đăng ký các khóa học luyện đề online đắt tiền trên mạng không?",
                "Làm sao để kiểm soát sự buồn ngủ rũ rượi mỗi khi ngồi vào bàn học vào buổi chiều?",
                "Mẹo tóm tắt một chương sách dài thành bản đồ tư duy ngắn gọn, dễ nhớ?",
                "Việc đọc lại sách giáo khoa có còn giá trị trong giai đoạn luyện đề nâng cao không?",
                "Làm sao để cân bằng giữa việc học kiến thức mới và việc ôn tập lại kiến thức cũ?",
                "Có nên vừa học vừa nghe nhạc không lời để tăng khả năng tập trung không?",
                "Làm sao để vượt qua cảm giác sợ hãi mỗi khi giáo viên gọi lên bảng kiểm tra bài cũ?",
                "Mình bị áp lực vì bạn bè xung quanh đều đã xuất phát sớm, còn mình chỉ mới bắt đầu.",
                "Có nên sử dụng các ứng dụng quản lý thời gian (như Forest, Notion) để hỗ trợ việc học không?"
            ],
            'Gia đình': [
                "Bố mẹ lúc nào cũng so sánh mình với mấy bạn giỏi, mình nên mở lời thế nào để bố mẹ hiểu?",
                "Mình thấy không gian ở nhà rất ngột ngạt, mọi cuộc nói chuyện đều dẫn đến cãi vã thì phải làm sao?",
                "Mình muốn tâm sự với gia đình về áp lực hiện tại nhưng sợ bị nói là yếu đuối, kém cỏi.",
                "Bố mẹ không chịu nghe mình giải thích mà lúc nào cũng áp đặt, làm sao để thay đổi điều này?",
                "Bố mẹ luôn mang sự vất vả của họ ra để ép mình phải theo ý họ, mình cảm thấy áp lực quá.",
                "Cứ mỗi lần gia đình họp mặt là mọi người lại lấy điểm số của mình ra bàn tán, làm sao để mình đối mặt?",
                "Bố mẹ hay soi xét quyền riêng tư như đọc tin nhắn, kiểm tra nhật ký của mình, làm sao để thiết lập ranh giới?",
                "Bố mẹ không bao giờ công nhận nỗ lực của mình mà chỉ nhìn vào kết quả, làm sao để mình ngừng chạnh lòng?",
                "Gia đình mình không có điều kiện kinh tế nên mình thấy rất áp lực về học phí đại học, có cách nào tháo gỡ không?",
                "Bố mẹ lúc nào cũng coi mình là đứa trẻ con không biết gì, làm sao để họ công nhận sự trưởng thành của mình?",
                "Mình cảm thấy bố mẹ thiên vị anh/chị/em hơn mình rất nhiều, cảm giác này tổn thương quá.",
                "Làm sao để từ chối những kỳ vọng quá tầm tay mà gia đình đang đặt lên vai mình?",
                "Bố mẹ cấm mình tham gia các hoạt động ngoại khóa vì sợ ảnh hưởng học tập, thuyết phục thế nào?",
                "Làm sao để mở lời xin lỗi bố mẹ sau một cuộc cãi vã nảy lửa mà không thấy ngượng ngùng?",
                "Bố mẹ không tôn trọng quyết định cá nhân của mình từ việc ăn mặc đến sở thích, phải làm sao?",
                "Mình thấy mình và bố mẹ ở hai thế giới hoàn toàn khác nhau, không thể tìm thấy tiếng nói chung.",
                "Bố mẹ kiểm soát quá mức từ giờ giấc đi lại đến bạn bè mình chơi cùng, làm sao để xin thêm tự do?",
                "Mỗi khi mình làm sai điều gì, bố mẹ lại nhắc lại những lỗi lầm trong quá khứ, cách nào để chấm dứt?",
                "Bố mẹ không tin tưởng vào năng lực tự học của mình mà bắt đi học thêm liên tục, xử lý thế nào?",
                "Bố mẹ bắt mình phải ở nhà dọn dẹp và chăm sóc em quá nhiều làm ảnh hưởng giờ học, phải làm sao?",
                "Làm thế nào để giải thích cho bố mẹ hiểu về những căn bệnh tâm lý mà giới trẻ đang gặp phải?",
                "Bố mẹ hay tự ý quyết định mọi chuyện lớn nhỏ trong cuộc sống của mình mà không hỏi ý kiến.",
                "Mình cảm thấy ngôi nhà không còn là nơi an toàn để mình trở về sau những giờ học mệt mỏi.",
                "Bố mẹ giận dỗi và dùng chiêu trò im lặng với mình nhiều ngày liền, làm sao phá tan băng?",
                "Làm sao để xử lý tình huống khi bố mẹ xúc phạm sở thích và cá tính riêng của mình?",
                "Bố mẹ luôn áp đặt tư duy thời ngày xưa vào hoàn cảnh sống hiện tại của mình, giải thích sao đây?",
                "Làm thế nào để giữ được sự bình tĩnh khi bố mẹ vô tình nói ra những lời làm tổn thương mình?",
                "Bố mẹ không cho phép mình có bạn khác giới vì sợ yêu sớm, làm sao để giải tỏa sự vô lý này?",
                "Làm sao để phản bác lại những quan điểm sai lầm của bố mẹ mà vẫn giữ được sự lễ phép?",
                "Bố mẹ hay mang những chuyện thầm kín của mình ra làm trò đùa trước mặt người ngoài.",
                "Mình cảm thấy mình đang phải sống cuộc đời mà bố mẹ vẽ ra chứ không phải cuộc đời của mình.",
                "Bố mẹ không chịu cập nhật những thông tin mới về thi cử và cứ bắt mình làm theo cách cũ.",
                "Làm sao để bố mẹ hiểu rằng mình cần có khoảng không gian riêng tư vào buổi tối?",
                "Bố mẹ luôn nghi ngờ mình nói dối mỗi khi mình xin phép đi học nhóm hoặc tham gia sự kiện.",
                "Mình cảm thấy có khoảng cách rất lớn với gia đình vì mình là con nuôi/con riêng.",
                "Bố mẹ hay đổ lỗi cho việc mình dùng điện thoại là nguyên nhân của mọi thất bại trong cuộc sống.",
                "Làm sao để chia sẻ với bố mẹ về định hướng giới tính của mình mà không làm họ sốc?",
                "Mình cảm thấy áp lực vì phải làm tấm gương hoàn hảo cho các em trong nhà.",
                "Bố mẹ hay đem thành công của con cái người khác ra để làm mình thấy hổ thẹn.",
                "Làm sao để xây dựng lại niềm tin với bố mẹ sau khi mình đã lỡ làm sai một điều lớn?",
                "Bố mẹ không đồng ý cho mình theo đuổi ước mơ vì cho rằng ngành đó không sang trọng.",
                "Làm sao để học cách yêu thương bố mẹ dù giữa hai thế hệ có quá nhiều điểm bất đồng?"
            ],
            'Tình cảm': [
                "Lớp (10,11,12) rồi mà mình vẫn vướng vào chuyện tình cảm khiến học hành sa sút, mình phải xử lý sao đây?",
                "Sắp ra trường và mỗi đứa một nơi, mình cảm thấy rất sợ cảm giác phải chia xa bạn thân.",
                "Mình vừa chia tay, cảm giác rất đau khổ và không thể tập trung học được thì phải làm sao?",
                "Mình lỡ thích bạn thân nhưng sợ thổ lộ xong thì mất luôn tình bạn đẹp này.",
                "Cảm giác yêu đơn phương một người tốn năng lượng quá, làm sao để mình buông bỏ?",
                "Bạn bè xung quanh ai cũng có đôi có lứa làm mình thấy tủi thân và cô đơn, liệu mình có vấn đề gì không?",
                "Mình bị người ta cắt liên lạc đột ngột, cảm giác bị bỏ rơi này làm sao để vượt qua?",
                "Bị crush phớt lờ khiến mình suy sụp tinh thần mấy ngày nay, làm sao để lấy lại năng lượng học tập?",
                "Tụi mình hứa cùng vào một trường đại học nhưng điểm chênh lệch quá, mình có nên dừng lại?",
                "Mình phát hiện người yêu mình đang nhắn tin mập mờ với người khác, xử lý sao?",
                "Làm sao để cân bằng giữa việc dành thời gian cho người yêu/bạn bè và việc tập trung ôn thi đại học?",
                "Mình bị bạn bè trong lớp hiểu lầm và cô lập, làm sao để vượt qua quãng thời gian đi học này?",
                "Làm thế nào để thoát khỏi một mối quan hệ mập mờ khiến mình mệt mỏi?",
                "Bạn bè chơi chung nhóm bắt đầu có sự đố kỵ và nói xấu sau lưng nhau, mình nên rút lui thế nào?",
                "Mình thích một người nhưng người đó lại thích người khác, tình huống này trớ trêu quá.",
                "Làm sao để không bị cảm xúc tình cảm chi phối khiến bản thân đưa ra những quyết định bồng bột?",
                "Làm thế nào để hàn gắn mối quan hệ bạn thân sau một lần cãi vã lớn về quan điểm sống?",
                "Mình lỡ làm người khác tổn thương trong tình cảm và bây giờ cảm thấy rất dằn vặt, làm sao để hết?",
                "Cảm giác cô đơn ngay cả khi đang đứng giữa một tập thể lớp đông đúc là vì sao?",
                "Bạn bè dạo này chỉ tìm đến mình khi cần nhờ vả học tập chứ bình thường không ai hỏi thăm.",
                "Làm sao để phân biệt giữa tình cảm tuổi học trò nhất thời và tình yêu nghiêm túc?",
                "Mình cảm thấy mình luôn là người phải chủ động duy trì mối quan hệ bạn bè, nếu mình im lặng thì mọi thứ kết thúc.",
                "Cảm giác sợ bị bỏ rơi khiến mình luôn cố gắng làm hài lòng người yêu một cách vô điều kiện.",
                "Làm sao để giữ tâm lý vững vàng khi thấy người cũ đã nhanh chóng có tình mới?",
                "Bạn bè lấy điểm số và khuyết điểm ngoại hình của mình ra để làm trò đùa, mình nên phản ứng ra sao?",
                "Mình cảm thấy không ai trong lớp thực sự hiểu và tôn trọng cá tính riêng của mình.",
                "Làm sao để vượt qua sự tự ti về ngoại hình khi đứng trước người mình thích?",
                "Làm sao để không đem những cảm xúc bực bội từ chuyện tình cảm đổ lên đầu gia đình và bạn bè?",
                "Mình bị lôi vào cuộc chiến phe phái trong lớp dù mình chỉ muốn yên ổn học tập.",
                "Bạn thân cố tình tiết lộ bí mật riêng tư của mình cho người khác, mình nên đối mặt thế nào?",
                "Mình cảm thấy mình quá nhạy cảm và dễ bị tổn thương bởi những lời nói vô tình của bạn bè.",
                "Làm thế nào để ngừng việc stalk mạng xã hội của crush hay người cũ?",
                "Mình thích một người cùng giới nhưng không dám công khai vì sợ bạn bè kỳ thị, xử lý thế nào?",
                "Bạn bè chỉ quan tâm đến những bạn học giỏi hoặc giàu có, mình cảm thấy bị xem thường.",
                "Làm sao để thiết lập lại một tình bạn thuần khiết sau khi tỏ tình thất bại?",
                "Mình cảm thấy người yêu chỉ coi mình là phương án dự phòng, làm sao để chấm dứt dứt khoát?",
                "Khi năm học cấp 3 khép lại, làm thế nào để lưu giữ những kỷ niệm đẹp mà không bị chìm đắm trong sự luyến tiếc?"
            ],
            'Định hướng': [
                "(16,17,18) tuổi mà mình vẫn chưa biết mình thích gì hay hợp với ngành nào thì có sao không?",
                "Bố mẹ muốn mình chọn ngành an toàn, nhưng mình lại muốn mạo hiểm theo đam mê thì nên làm thế nào?",
                "Mình sợ chọn sai ngành ở tuổi 18 sẽ phá hỏng cả tương lai, làm sao để bớt hoảng loạn?",
                "Giữa việc chọn ngành mình giỏi và ngành mình thích nhưng học chưa tốt thì mình nên ưu tiên cái nào?",
                "Ngành học mình thích lại khó kiếm tiền trong tương lai, mình có nên thực tế hơn không?",
                "Làm sao để mình tự đánh giá đúng năng lực của bản thân xem có hợp với ngành mình chọn không?",
                "Nếu mình chọn học một ngành đang 'hot' nhưng đến lúc ra trường nó hết 'hot' thì sao?",
                "Mình có nên chấp nhận học một trường tư thục đắt đỏ để theo đúng ngành mình thích không?",
                "Làm sao để biết mình thực sự thích ngành mình chọn?",
                "Nếu mình muốn học nghề hoặc đi làm luôn thay vì học đại học thì có bị xem là thất bại không?",
                "Sự phát triển của AI có khiến ngành mình dự định học bị biến mất trong vài năm tới không?",
                "Bố mẹ bảo ngành mình chọn không phù hợp với giới tính/tính cách của mình, làm sao để thuyết phục họ?",
                "Làm sao để biết một công việc có triển vọng nghề nghiệp lâu dài hay chỉ là xu hướng ngắn hạn?",
                "Mình thích quá nhiều thứ cùng lúc và cái gì cũng muốn học, làm sao để thu hẹp lựa chọn?",
                "Làm thế nào để nói chuyện thẳng thắn với gia đình về việc mình không muốn tiếp quản công việc kinh doanh của nhà?",
                "Làm sao để nhận biết được đâu là năng khiếu thật sự và đâu chỉ là sở thích nhất thời?",
                "Nếu mình theo đuổi ngành ... thì cần chuẩn bị tâm lý cho những khó khăn gì?",
                "Bố mẹ không ủng hộ mình thi vào các trường ..., mình nên xử lý thế nào?",
                "Làm sao để biết môi trường học tập của một trường đại học có phù hợp với tính cách của mình không?",
                "Có nên chọn ngành học chỉ vì bạn thân của mình cũng đăng ký ngành đó không?",
                "Làm sao để dung hòa giữa ước mơ của bản thân và tính khả thi về mặt tài chính của gia đình?",
                "Bố mẹ bắt mình phải nộp hồ sơ vào ngành ... để dễ xin việc, nhưng mình không thích thì làm sao?"
            ],
            'Cảm xúc': [
                "Dạo này mình rất hay vô cớ gắt gỏng hoặc muốn khóc mà không rõ lý do, đây là biểu hiện gì?",
                "Cảm giác trống rỗng, không vui cũng chẳng buồn kéo dài nhiều ngày liền là sao vậy?",
                "Mình luôn thấy hoảng loạn quá mức trước mỗi lần trả bài hay làm đề thi, liệu mình có gặp vấn đề tâm lý không?",
                "Làm sao để phân biệt giữa nỗi buồn tạm thời và dấu hiệu của trầm cảm?",
                "Tại sao mỗi khi stress mình lại có xu hướng ăn rất nhiều hoặc bỏ bữa hoàn toàn?",
                "Cảm giác tim đập nhanh, tay chân run rẩy mỗi khi đến giờ kiểm tra là tâm lý gì?",
                "Mình rất hay bị rơi vào trạng thái suy nghĩ quá nhiều vào đêm muộn, nguyên nhân do đâu?",
                "Việc mình hay giấu kín cảm xúc tiêu cực và luôn giả vờ vui vẻ trước mặt người khác có nguy hiểm không?",
                "Cảm giác tê liệt cảm xúc, không thấy đau khổ mà cũng chẳng thấy vui khi nhận điểm kém là vì sao?",
                "Việc mình luôn cảm thấy tội lỗi mỗi khi ngồi chơi hoặc đi ngủ sớm là dấu hiệu của loại áp lực nào?",
                "Tại sao mình lại hay mơ thấy những viễn cảnh tồi tệ như thi trượt hay bị mọi người quay lưng?",
                "Cảm giác bồn chồn, đứng ngồi không yên dù không có sự việc gì cụ thể xảy ra phản ánh điều gì?",
                "Tại sao mỗi lần gặp áp lực mình lại có xu hướng muốn gãi đập hoặc tự làm đau bản thân?",
                "Hiện tượng trì hoãn do quá sợ thất bại có phải là một dạng rối loạn tâm lý?",
                "Tại sao mình lại cảm thấy kiệt sức ngay cả khi mình không làm gì cả ngày?",
                "Cảm giác mình đang xem cuộc đời mình như một bộ phim chứ không thực sự sống trong đó là sao? (derealization)",
                "Sự tức giận bộc phát đột ngột khi ai đó đụng vào đồ đạc của mình thể hiện trạng thái dồn nén gì?",
                "Tại sao mình lại bị mất khả năng tập trung hoàn toàn dù không gian xung quanh rất yên tĩnh?",
                "Cảm giác khinh thường bản thân mỗi khi nhìn vào gương xuất phát từ nguyên nhân nào?",
                "Tại sao mình lại luôn muốn tìm kiếm sự hoàn hảo tuyệt đối trong từng mọi thứ?",
                "Cảm giác bị ngợp trước quá nhiều thông tin và nhiệm vụ cần làm xử lý góc độ tâm lý ra sao?",
                "Tại sao mình lại hay có suy nghĩ tiêu cực về tương lai dù kết quả học tập hiện tại vẫn tốt?",
                "Sự mất đi hứng thú đột ngột với những sở thích cũ (nghe nhạc, chơi game, vẽ tranh) nói lên điều gì?",
                "Tại sao mình lại hay so sánh bản thân với những kịch bản không có thật trên mạng xã hội?",
                "Sự thay đổi tâm trạng thất thường từ cực kỳ hưng phấn sang cực kỳ suy sụp trong một ngày là dấu hiệu gì?",
                "Cảm giác luôn có một nỗi sợ mơ hồ rình rập mình mọi lúc mọi nơi gọi là gì?",
                "Tại sao việc nhận lời khen từ người khác lại làm mình cảm thấy xấu hổ và không thoải mái?",
                "Sự thèm khát được ngủ liên tục 12-14 tiếng một ngày có phải là cơ chế tự vệ của não bộ?",
                "Cảm giác mất kết nối với bạn bè thân thiết dù vẫn trò chuyện hàng ngày giải thích thế nào?",
                "Tại sao mình lại hay nảy sinh ý định bỏ đi thật xa mỗi khi mâu thuẫn gia đình đỉnh điểm?",
                "Hiện tượng tự tạo ra các cuộc tranh luận giả tưởng trong đầu và tự làm mình bực mình là sao?",
                "Cảm giác tội lỗi khi tiêu tiền của bố mẹ vào việc giải trí cá nhân phản ánh tâm lý gì?",
                "Tại sao mình lại luôn thấy mình là nạn nhân trong mọi cuộc tranh cãi?",
                "Cảm giác mình phải mang một 'mặt nạ' khác nhau khi gặp những nhóm người khác nhau có bình thường không?",
                "Tại sao mỗi lần đối mặt với thử thách mới, phản ứng đầu tiên của mình luôn là muốn bỏ cuộc?",
                "Sự thèm muốn sự chú ý từ người khác nhưng khi được chú ý lại thấy phiền phức là tâm lý gì?",
                "Cảm giác đau đầu, đau dạ dày thường xuyên vào các mốc thời gian cố định trong tuần có liên quan đến stress?",
                "Tại sao mình lại dễ tha thứ cho lỗi lầm của người khác nhưng lại cực kỳ hà khắc với chính mình?",
                "Sự sợ hãi không gian hẹp hoặc sự im lặng tuyệt đối trong phòng thi giải mã thế nào?",
                "Cảm giác mình đang bị theo dõi hoặc đánh giá bởi những người xung quanh là do đâu?",
                "Tại sao việc thiết lập mục tiêu lại khiến mình thấy áp lực hơn là không có mục tiêu nào?",
                "Sự nghiện cảm giác an toàn đến mức không dám thử bất kỳ trải nghiệm mới nào nói lên điều gì?",
                "Cảm giác mất niềm tin hoàn toàn vào sự chân thành của con người xung quanh là kết quả của điều gì?",
                "Tại sao mình lại hay bị ám ảnh bởi những sai lầm nhỏ nhặt từ nhiều năm trước?",
                "Cảm giác thấy mình trưởng thành quá nhanh so với lứa tuổi và phải gánh vác quá nhiều cảm xúc tiêu cực?"
            ],
            'Khuyên nhủ': [
                "Mình cảm thấy bản thân không có điểm mạnh gì nổi bật, làm sao để thoát khỏi sự tự ti này?",
                "Dạo này mình bị nghiện mạng xã hội và lướt điện thoại vô thức hàng giờ, mình nên làm gì để dừng lại?",
                "Mình rất sợ cảm giác bị người khác đánh giá, làm sao để ngừng bận tâm về suy nghĩ của người khác?",
                "Tự nhiên mình thấy mất phương hướng hoàn toàn, không biết phải bắt đầu sắp xếp lại cuộc sống từ đâu?",
                "Mỗi lần thất bại hay làm sai điều gì, mình lại tự dằn vặt bản thân rất lâu, làm sao để tha thứ cho chính mình?",
                "Mình hay trì hoãn đến phút chót mới chịu làm, làm sao để rèn luyện tính kỷ luật?",
                "Mình luôn cảm thấy áp lực phải hoàn hảo trong mắt mọi người, điều này khiến mình đuối sức quá.",
                "Làm sao để đặt ra ranh giới với những người bạn luôn tìm đến mình chỉ để xả năng lượng tiêu cực?",
                "Nhiều lúc mình chỉ muốn trốn chạy khỏi thực tại một thời gian, làm sao để vượt qua cảm giác này?",
                "Mình bị áp lực đồng lứa nặng quá, thấy ai cũng giỏi giang còn mình dậm chân tại chỗ thì phải làm sao?",
                "Cứ mỗi lần chuẩn bị làm điều gì mới là mình lại nghĩ đến kịch bản tồi tệ nhất, làm sao để bớt tiêu cực?",
                "Mình cảm thấy cuộc sống hiện tại rất đơn điệu và vô nghĩa, làm sao để tìm lại niềm vui sống?",
                "Mỗi khi gặp khó khăn mình đều có xu hướng thu mình lại và không muốn nhờ ai giúp đỡ, điều này có tốt không?",
                "Làm sao để học cách chấp nhận những thứ vượt ngoài tầm kiểm soát của mình?",
                "Mình hay so sánh bản thân của hiện tại với quá khứ và thấy mình tệ đi, làm sao để thoát khỏi cái bẫy này?",
                "Khi tất cả mọi thứ cùng lúc sụp đổ thì mình nên ưu tiên xử lý điều gì trước?",
                "Làm sao để rèn luyện sự kiên nhẫn khi mình luôn muốn thấy kết quả ngay lập tức?",
                "Mình rất dễ bị ảnh hưởng bởi tâm trạng của người xung quanh, làm sao để giữ bình tĩnh cho riêng mình?",
                "Dạo này mình hay rơi vào trạng thái nghi ngờ chính giá trị của bản thân, mình cần lời khuyên gì lúc này?",
                "Làm sao để vượt qua sự lười biếng mang tính hệ thống chứ không phải chỉ là sự mệtỏi tạm thời?",
                "Mình hay tự tạo ra những tiêu chuẩn quá cao rồi tự làm mình thất vọng, cách nào để điều chỉnh lại?",
                "Khi cảm thấy cả thế giới đang quay lưng với mình thì mình nên tựa vào đâu?",
                "Làm thế nào để học cách từ chối lịch sự mà không cảm thấy tội lỗi?",
                "Mình rất muốn thay đổi bản thân nhưng lại sợ bước ra khỏi vùng an toàn, làm sao để lấy đà?",
                "Làm sao để giữ được sự tử tế và lòng tin vào con người khi từng bị phản bội nhiều lần?",
                "Mỗi khi đứng trước quyết định lớn, mình thường bị đóng băng vì sợ chọn sai, xử lý thế nào?",
                "Mình luôn thấy mình là phiên bản lỗi so với kỳ vọng của mọi người, làm sao để gạt bỏ gánh nặng này?",
                "Làm sao để cân bằng giữa sự nghiêm khắc với bản thân và việc biết tự vỗ về khi mệt mỏi?",
                "Dạo này mình bị mất khả năng lắng nghe và dễ nổi giận vô cớ, làm sao để điềm đạm trở lại?",
                "Mình muốn tìm một sở thích giúp chữa lành tinh thần nhưng không biết bắt đầu từ đâu?",
                "Có cách nào để biến sự ghen tị thành động lực phát triển bản thân thay vì tự dằn vặt không?",
                "Mình cảm thấy mình đang sống quá vội vã và bỏ lỡ nhiều khoảnh khắc đẹp, làm sao để sống chậm lại?",
                "Làm sao để đối diện với nỗi sợ cô đơn khi bạn bè dần có những hướng đi riêng?",
                "Mình rất hay dồn nén cảm xúc cho đến khi bùng nổ, có phương pháp nào xả căng thẳng lành mạnh không?",
                "Cảm giác mình cố gắng 200% nhưng kết quả vẫn thua người chỉ cố gắng 50%, làm sao để không bất mãn?",
                "Mình nên làm gì khi nhận ra những mục tiêu mình đặt ra từ đầu năm giờ không còn phù hợp nữa?",
                "Mình muốn bắt đầu thói quen viết nhật ký để giải tỏa nhưng cứ viết được vài ngày lại bỏ, làm sao để duy trì?",
                "Mình hay bị dồn vào thế phải đưa ra quyết định thay cho người khác, làm sao để thoát khỏi vai trò này?",
                "Khi niềm tin vào bản thân chạm đáy, điều đầu tiên mình nên làm là gì?",
                "Làm sao để phân biệt được đâu là lời góp ý chân thành và đâu là sự công kích cá nhân?",
                "Mình luôn cảm thấy quỹ thời gian trong ngày không bao giờ là đủ, làm sao để sống thong dong hơn?",
                "Cảm giác mình luôn phải gồng mình lên để tỏ ra mạnh mẽ khiến mình rất mệt, làm sao để sống thật?",
                "Làm sao để đối phó với cảm giác nuối tiếc những cơ hội mình đã bỏ lỡ trong quá khứ?",
                "Mình nên làm gì khi cảm thấy những lời khuyên từ người lớn không còn phù hợp với thực tế của mình?",
                "Làm thế nào để tự tạo ra động lực nội tại thay vì phụ thuộc vào lời khen chê từ bên ngoài?"
            ]
        },
        'Phụ huynh': {
            'Tâm lý': [
                "Tâm lý của học sinh lớp 12 chuẩn bị thi đại học thường có những đặc điểm gì?",
                "Tại sao con ở độ tuổi này lại trở nên khép kín, ít chia sẻ và hay giận dỗi với cha mẹ?",
                "Nhu cầu được tôn trọng sự riêng tư và khẳng định bản thân của con tuổi (16,17,18) biểu hiện như thế nào?",
                "Nỗi sợ thất bại và sợ làm cha mẹ thất vọng ảnh hưởng như thế nào đến tâm lý thi cử của con?",
                "Hiện tượng chống đối ngầm ở lứa tuổi 17-18 biểu hiện như thế nào trong sinh hoạt hàng ngày?",
                "Tại sao con lại coi trọng ý kiến của bạn bè hơn là lời khuyên chân thành từ cha mẹ?",
                "Tâm lý sợ bỏ lỡ và áp lực thành tích trên mạng xã hội ảnh hưởng thế nào đến con?",
                "Tâm lý muốn làm người lớn nhưng năng lực kiểm soát cảm xúc chưa đủ chín chắn ở tuổi 18 biểu hiện ra sao?",
                "Khủng hoảng bản sắc tuổi 18 ảnh hưởng thế nào đến cách con lựa chọn tương lai?"
            ],
            'Hành vi': [
                "Con dạo này hay đóng chặt cửa phòng, đập phá đồ đạc khi giận tôi nên làm gì?",
                "Con thức rất khuya xem điện thoại, điểm số sa sút đột ngột là dấu hiệu của vấn đề tâm lý nào?",
                "Việc con tự cô lập bản thân, bỏ ăn hoặc có dấu hiệu tự làm đau mình có ý nghĩa gì?",
                "Con thường xuyên nói dối về kết quả học tập, cha mẹ nên hiểu hành vi này như thế nào?",
                "Con thường xuyên gạt phắt đi hoặc nổi nóng mỗi khi cha mẹ hỏi về chuyện học hành/thi cử có nghĩa là gì?",
                "Con đột nhiên thay đổi phong cách ăn mặc, nhuộm tóc nổi bật hoặc xăm hình ở tuổi 18 thể hiện điều gì?",
                "Con hay than thở 'sống không có ý nghĩa' hoặc 'mệt mỏi với cuộc sống', đây có phải là lời cảnh báo nguy hiểm?",
                "Con có biểu hiện chống đối bằng cách im lặng tuyệt đối mỗi khi gia đình nhắc đến chuyện thi cử nghĩa là gì?",
                "Con dành quá nhiều thời gian tham gia các hội nhóm tiêu cực trên mạng xã hội phản ánh thiếu hụt tâm lý nào?",
                "Con bắt đầu có hành vi giấu giếm, nói dối về việc đi đâu, làm gì sau giờ học có phải dấu hiệu hư hỏng?",
                "Con ăn uống thất thường, lúc ăn rất nhiều lúc lại bỏ bữa liên tục là biểu hiện của rối loạn gì?",
                "Việc con tự dọn dẹp phòng xá sạch sẽ lạ thường và mang cho đi những đồ vật yêu thích cảnh báo điều gì?",
                "Con giật mình giấu điện thoại mỗi khi cha mẹ bước vào phòng phản ánh tâm lý nghi ngờ hay giấu giếm gì?",
                "Con liên tục đòi hỏi những khoản tiền lớn mà không đưa ra được lý do rõ ràng ẩn chứa nguy cơ gì?",
                "Con bắt đầu sử dụng thuốc lá điện tử hoặc chất kích thích trong phòng riêng thể hiện sự bế tắc gì?",
                "Con thường xuyên than đau đầu, đau bụng vào đúng giờ chuẩn bị đi học thêm nói lên điều gì?",
                "Việc con liên tục gãi bóc da tay, nhổ tóc đến mức chảy máu là hành vi giải tỏa stress ra sao?",
                "Con bỏ học đi chơi game xuyên đêm nhưng vẫn nói dối là đi học nhóm ẩn chứa nỗi sợ nào?",
                "Con phản ứng dữ dội và khóc nức nở chỉ vì một lời góp ý rất nhỏ của cha mẹ thể hiện ngưỡng chịu đựng ra sao?",
                "Việc con từ chối tham gia tất cả các chuyến du lịch hay bữa ăn chung của gia đình phản ánh điều gì?",
                "Con mua rất nhiều thực phẩm chức năng hoặc thuốc không rõ nguồn gốc trên mạng về uống có ý nghĩa gì?",
                "Con xé bỏ các bài kiểm tra điểm kém hoặc giấu giếm bảng điểm phản ánh áp lực gì?",
                "Việc con bắt đầu có thái độ hỗn xược và thách thức 'bố mẹ đánh con đi' thể hiện tâm lý bất cần nào?",
                "Con dành hàng giờ nhìn chằm chằm vào khoảng trống mà không làm gì cả phản ánh sự trống rỗng ra sao?",
                "Việc con liên tục thay đổi mật khẩu điện thoại và máy tính với thái độ cực kỳ cảnh giác?",
                "Con gạch xóa chằng chịt hoặc viết những lời tiêu cực vào sách vở học tập thể hiện sự giải tỏa gì?",
                "Con đột nhiên cắt đứt liên lạc với toàn bộ nhóm bạn thân cũ và chơi với nhóm bạn hoàn toàn mới?",
                "Việc con luôn cố tình đi ngủ thật muộn để né tránh việc phải giáp mặt cha mẹ vào buổi tối?",
                "Con có thói quen mua sắm vô độ trên các sàn thương mại điện tử dù không dùng đến đồ đạc đó?",
                "Việc con giấu vết thương ở cổ tay bằng cách luôn mặc áo dài tay giữa mùa hè nóng bức?",
                "Con hay bị giật mình, hoảng hốt và toát mồ hôi hột khi nghe tiếng chuông điện thoại hoặc tiếng gõ cửa?",
                "Việc con liên tục từ chối ăn cơm chung và chỉ đòi bê bát đĩa về phòng riêng ăn một mình?",
                "Con bắt đầu nói về những chủ đề tâm linh, cái chết hoặc sự giải thoát một cách thản nhiên?",
                "Việc con thu thập các vật sắc nhọn (dao, kéo, lưỡi lam) giấu dưới gối hoặc trong hộc bàn?",
                "Con phản ứng thờ ơ, không chút cảm xúc khi bị cha mẹ mắng chửi nặng lời là dấu hiệu của điều gì?",
                "Việc con bỏ bê hoàn toàn môn học chuyên trường để dồn toàn bộ thời gian vào một sở thích kỳ lạ?",
                "Con liên tục kiểm tra lại khóa cửa, vòi nước nhiều lần trước khi đi ngủ phản ánh sự lo âu nào?",
                "Việc con bắt đầu có hành vi ngược đãi hoặc xua đuổi thú cưng trong nhà khi căng thẳng?",
                "Con xóa hết toàn bộ bài đăng và hình ảnh cá nhân trên mạng xã hội thể hiện tâm lý muốn biến mất nào?",
                "Việc con tự ý bỏ các buổi học chính khóa ở trường để lang thang ở các quán cà phê?",
                "Con hay giật tóc, đấm vào tường hoặc tự tát vào mặt mình mỗi khi giải không được bài tập?",
                "Việc con liên tục soi gương và phàn nàn về từng khuyết điểm nhỏ trên cơ thể với thái độ ám ảnh?",
                "Con bắt đầu theo dõi các trang mạng có nội dung bạo lực, tự sát hoặc tư tưởng lệch chuẩn?",
                "Con tỏ ra cực kỳ vâng lời một cách máy móc nhưng ánh mắt hoàn toàn vô hồn, không chút sức sống?",
                "Việc con cố tình làm hỏng đồ đạc đắt tiền mà cha mẹ mới mua cho để chứng tỏ điều gì?",
                "Con nói chuyện một mình trong phòng kín hoặc có những điệu bộ kỳ quặc khi căng thẳng?",
                "Việc con tuyệt đối không bao giờ nhắc đến tên các bạn cùng lớp hay chuyện trường lớp khi về nhà?",
                "Con có biểu hiện gom góp và cất giấu các loại thuốc tây trong nhà vào một hộp riêng?"
            ],
            'Thấu hiểu': [
                "Làm thế nào để mở lời trò chuyện với con khi con luôn tỏ ra chống đối và thu mình lại?",
                "Đặt câu hỏi như thế nào để con cảm thấy an toàn, không bị phán xét và chịu chia sẻ với bố mẹ?",
                "Làm sao để cân bằng giữa việc theo sát con học tập và tôn trọng quyền riêng tư của con?",
                "Làm sao để nhận biết con đang gặp áp lực nặng nề ở trường mà con không chịu nói ra?",
                "Cha mẹ nên dùng thái độ nào khi con nhận kết quả thi thử không tốt để không làm con tổn thương thêm?",
                "Làm thế nào để cha mẹ học cách chấp nhận rằng ước mơ của con khác hoàn toàn kỳ vọng của mình?",
                "Làm sao để tạo cho con cảm giác ngôi nhà là nơi an toàn nhất để con tìm về mỗi khi gặp thất bại?",
                "Cách khen ngợi và động viên con đúng cách ở tuổi 18 mà không gây tác dụng ngược hay tạo thêm áp lực?",
                "Làm sao để cha mẹ giữ được sự bình tĩnh và không nổi giận khi con cố tình nói những lời thách thức?"
            ],
            'Hành động': [
                "Tôi nên làm gì ngay khi phát hiện con có dấu hiệu bị căng thẳng kịch liệt, lo âu hoặc trầm cảm?",
                "Khi thấy con bị xao nhãng học hành vì chuyện tình cảm tuổi học trò, cha mẹ nên xử lý thế nào cho khéo?",
                "Cha mẹ cần chuẩn bị và hành động ra sao để giúp con giảm áp lực trong kỳ thi quyết định sắp tới?",
                "Nên phản ứng thế nào khi con công khai thiên hướng tình dục với gia đình?",
                "Cha mẹ nên làm gì khi con kiên quyết chọn một ngành học mà gia đình biết chắc chắn ra trường sẽ rất vất vả?",
                "Cần xử lý thế nào khi phát hiện con bị bắt nạt hội đồng hoặc thao túng tâm lý ở môi trường học đường?",
                "Cha mẹ cần hành động ra sao khi con có biểu hiện hoảng loạn ngay trước ngày thi?",
                "Phụ huynh nên can thiệp như thế nào khi con quá nghiện game hoặc mê idol đến mức bỏ bê kỳ thi?",
                "Tôi phải làm gì nếu con kiên quyết từ chối gặp chuyên gia tư vấn tâm lý dù con đang trong tình trạng rất tồi tệ?",
                "Cha mẹ nên xử lý thế nào khi phát hiện con có hành vi sử dụng chất kích thích hoặc thuốc lá điện tử?"
            ]
        }
    },
    'en': {
        'Student': {
            'Study': [
                "There is only a little time left before the exam, but my mind is still blank. Where should I start?",
                "I get easily distracted by my phone when studying. How can I fix this?",
                "I learn and forget quickly, my brain feels sluggish lately. How can I improve my memory?",
                "How to overcome exhaustion when studying day and night continuously?",
                "I've lost my foundation in [Subject]. Is it too late to catch up in 12th grade?",
                "Are the Pomodoro or Active Recall methods really effective for graduation exam prep?",
                "How to stay focused when self-studying at home without being tempted by my bed?",
                "My packed tutoring schedule leaves me no time for self-study. How should I rearrange it?",
                "The closer the exam gets, the more I feel like I've forgotten everything. Is this normal?",
                "How to overcome the disappointment when my recent mock exam score is lower than before?",
                "I just can't swallow rote-learning subjects like History/Geography. Any quick learning tips?",
                "Studying without making progress makes me want to give up. How do I get my motivation back?",
                "Should I prioritize doing practice tests or reviewing basic theories during this final sprint?",
                "How to reasonably allocate time between combination exam subjects and prerequisite subjects?",
                "Does staying up until 2-3 AM to study actually yield better results than waking up early?",
                "Should I use brain-boosting pills or supplements to enhance my memory?",
                "How to stop procrastinating and waiting until the last minute to do homework/study?",
                "My home environment is too noisy to focus. Are there any alternative solutions?",
                "How to keep my eyes from getting tired and my brain from freezing up after hours of studying?",
                "Is it better to form a study group with friends or self-study alone?",
                "How to memorize complex Math/Physics/Chemistry formulas without rote learning?",
                "Should I drop some subjects that aren't in my university entrance block to focus my energy?",
                "When feeling overwhelmed with knowledge, how long should I completely rest to recover?",
                "How to find inspiration to study subjects that I absolutely hate?",
                "Should I sign up for expensive online exam-prep courses?",
                "How to control extreme sleepiness when sitting down to study in the afternoon?",
                "Any tips for summarizing a long book chapter into a short, easy-to-remember mind map?",
                "Is rereading the textbook still valuable during the advanced practice test phase?",
                "How to balance learning new knowledge with reviewing old material?",
                "Should I listen to instrumental music while studying to increase concentration?",
                "How to overcome the fear of being called to the board by the teacher for a pop quiz?",
                "I feel pressured because my peers started preparing early, while I am just beginning.",
                "Should I use time management apps (like Forest, Notion) to support my studies?"
            ],
            'Family': [
                "My parents always compare me to high-achieving kids. How should I bring this up so they understand?",
                "The atmosphere at home is suffocating, every conversation leads to an argument. What should I do?",
                "I want to confide in my family about my current stress, but I'm afraid they'll call me weak.",
                "My parents won't listen to my explanations and always impose their views. How to change this?",
                "My parents always use their hardships to force me to obey them. I feel so pressured.",
                "Every time there's a family gathering, people gossip about my grades. How do I face this?",
                "My parents invade my privacy, like reading my texts or diary. How to set boundaries?",
                "My parents never acknowledge my efforts, only the results. How do I stop feeling hurt?",
                "My family struggles financially, so I'm very stressed about college tuition. Is there a way out?",
                "My parents treat me like a clueless child. How to make them acknowledge my maturity?",
                "I feel my parents heavily favor my sibling over me. It hurts so much.",
                "How to politely refuse the unrealistic expectations my family places on me?",
                "My parents forbid extracurricular activities, fearing they will affect my studies. How to persuade them?",
                "How to initiate an apology to my parents after a heated argument without feeling awkward?",
                "My parents don't respect my personal choices, from my clothes to my hobbies. What should I do?",
                "I feel like my parents and I live in two completely different worlds, with no common ground.",
                "My parents over-control everything, from curfews to the friends I hang out with. How to ask for more freedom?",
                "Every time I make a mistake, my parents bring up my past errors. How to make it stop?",
                "My parents don't trust my self-study abilities and force me into endless tutoring classes.",
                "My parents make me do too many chores and take care of my siblings, affecting my study time.",
                "How to explain to my parents about the psychological issues that young people are facing today?",
                "My parents arbitrarily make all the big and small decisions in my life without asking my opinion.",
                "I feel like home is no longer a safe place to return to after exhausting school hours.",
                "My parents get mad and give me the silent treatment for days. How to break the ice?",
                "How to handle the situation when my parents insult my hobbies and personal identity?",
                "My parents always impose their old-fashioned mindset on my current life. How to explain this to them?",
                "How to stay calm when my parents accidentally say things that hurt me?",
                "My parents don't allow me to have friends of the opposite sex, fearing early romance. How to ease this unreasonableness?",
                "How to debate my parents' wrong views while remaining respectful?",
                "My parents often make jokes about my private matters in front of outsiders.",
                "I feel like I'm living the life my parents drew out for me, not my own life.",
                "My parents refuse to update themselves on new exam information and force me to do things the old way.",
                "How to make my parents understand that I need some private space in the evening?",
                "My parents always suspect I'm lying whenever I ask to go to a study group or an event.",
                "I feel a huge distance from my family because I am an adopted/stepchild.",
                "My parents always blame my phone usage as the root cause of every failure in my life.",
                "How to come out to my parents about my sexual orientation without shocking them?",
                "I feel pressured to be the perfect role model for my younger siblings.",
                "My parents often use other people's children's success to make me feel ashamed.",
                "How to rebuild trust with my parents after I made a huge mistake?",
                "My parents don't let me pursue my dream career because they think it's not 'prestigious' enough.",
                "How to learn to love my parents despite the many disagreements between our two generations?"
            ],
            'Relationships': [
                "I'm in high school but still caught up in a romance that's ruining my grades. What should I do?",
                "Graduation is coming and everyone is going their separate ways. I'm terrified of parting with my best friend.",
                "I just went through a breakup. I'm heartbroken and can't focus on studying. What should I do?",
                "I accidentally caught feelings for my best friend, but I'm afraid confessing will ruin our beautiful friendship.",
                "Unrequited love is draining so much energy. How do I let go?",
                "All my friends are in relationships, making me feel pitiful and lonely. Is something wrong with me?",
                "Someone suddenly cut off all contact with me. How do I get over this feeling of abandonment?",
                "Being ignored by my crush has ruined my mood for days. How do I get my study energy back?",
                "We promised to get into the same university, but our score gap is too huge. Should I end it?",
                "I found out my partner is sending flirtatious texts to someone else. How should I handle this?",
                "How to balance spending time with my partner/friends and focusing on university prep?",
                "I'm misunderstood and isolated by my classmates. How do I survive the rest of my school days?",
                "How to escape a 'situationship' that is exhausting me?",
                "My friend group is starting to get jealous and talk behind each other's backs. How should I withdraw?",
                "I like someone, but they like someone else. This situation is so ironic.",
                "How to not let romantic emotions dictate my actions and make me do impulsive things?",
                "How to mend a relationship with a best friend after a huge fight over life views?",
                "I accidentally hurt someone romantically and now I feel deeply remorseful. How to get over it?",
                "Why do I feel lonely even when standing in the middle of a crowded classroom?",
                "Lately, my friends only reach out when they need help with schoolwork, never just to check in.",
                "How to distinguish between a fleeting teenage crush and serious love?",
                "I feel like I'm always the one keeping the friendship alive. If I stay silent, everything ends.",
                "The fear of abandonment makes me try to unconditionally please my partner.",
                "How to stay mentally strong when I see my ex already has a new partner?",
                "My friends make jokes about my grades and physical flaws. How should I react?",
                "I feel like no one in my class truly understands and respects my unique personality.",
                "How to overcome body image insecurities when standing in front of my crush?",
                "How to avoid taking my relationship frustrations out on my family and friends?",
                "I'm being dragged into class faction wars even though I just want to study in peace.",
                "My best friend intentionally leaked my secret to others. How should I confront them?",
                "I feel overly sensitive and easily hurt by the careless words of my friends.",
                "How to stop stalking the social media of my crush or my ex?",
                "I like someone of the same gender but dare not come out for fear of discrimination. What should I do?",
                "My friends only care about those who are smart or rich, leaving me feeling looked down upon.",
                "How to re-establish a pure friendship after a failed confession?",
                "I feel my partner only sees me as a backup plan. How to end it decisively?",
                "As high school ends, how to preserve beautiful memories without drowning in regret?"
            ],
            'Future': [
                "Is it okay if I'm (16,17,18) years old and still don't know what I like or which major suits me?",
                "My parents want me to choose a safe major, but I want to take a risk on my passion. What should I do?",
                "I'm terrified that choosing the wrong major at 18 will ruin my entire future. How to panic less?",
                "Between a major I'm good at and a major I love but struggle with, which should I prioritize?",
                "The major I love might not pay well in the future. Should I be more realistic?",
                "How do I accurately assess my own abilities to see if I fit the major I've chosen?",
                "What if I choose a 'hot' major now, but by the time I graduate, it's no longer 'hot'?",
                "Should I accept attending an expensive private university just to study the exact major I want?",
                "How to know if I genuinely like the major I've chosen?",
                "If I choose to go to vocational school or start working immediately instead of college, am I considered a failure?",
                "Will the development of AI cause the career I plan to study to disappear in a few years?",
                "My parents say my chosen major doesn't suit my gender/personality. How to persuade them?",
                "How to know if a job has long-term career prospects or is just a short-term trend?",
                "I'm interested in too many things at once and want to study everything. How to narrow down my choices?",
                "How to have a frank conversation with my family about not wanting to take over the family business?",
                "How to distinguish between true natural talent and just a temporary hobby?",
                "If I pursue the [Field] industry, what mental difficulties should I prepare for?",
                "My parents don't support my application to [University]. How should I handle this?",
                "How to know if a university's learning environment suits my personality?",
                "Should I choose a major just because my best friend is applying for it too?",
                "How to reconcile my personal dreams with my family's financial feasibility?",
                "My parents force me to apply for [Major] to get a job easily, but I hate it. What should I do?"
            ],
            'Emotions': [
                "Lately I get irritated for no reason or want to cry without knowing why. What is this a sign of?",
                "The feeling of emptiness, neither happy nor sad, lasting for days. What's going on?",
                "I always panic excessively before every oral test or exam. Do I have a psychological issue?",
                "How to differentiate between temporary sadness and signs of depression?",
                "Why do I tend to either binge eat or completely skip meals when I'm stressed?",
                "Heart palpitations and shaking limbs every time a test starts—what psychology is this?",
                "I often fall into a state of overthinking late at night. What is the cause?",
                "Is it dangerous that I always hide negative emotions and pretend to be happy in front of others?",
                "Emotional numbness, feeling neither pain nor joy when getting a bad grade. Why is this?",
                "Feeling guilty every time I relax or go to sleep early is a sign of what kind of pressure?",
                "Why do I often dream of worst-case scenarios like failing exams or being abandoned?",
                "Feeling restless and unable to sit still even when nothing specific is happening reflects what?",
                "Why do I have the urge to scratch, hit, or self-harm every time I'm under pressure?",
                "Is procrastination due to extreme fear of failure a type of psychological disorder?",
                "Why do I feel exhausted even on days when I do absolutely nothing?",
                "Feeling like I'm watching my life like a movie rather than living it. What is this? (derealization)",
                "Sudden outbursts of anger when someone touches my belongings indicate what kind of pent-up state?",
                "Why do I completely lose the ability to focus even when my surroundings are perfectly quiet?",
                "The feeling of despising myself every time I look in the mirror stems from what cause?",
                "Why do I always seek absolute perfection in every single thing?",
                "Feeling overwhelmed by too much information and tasks—how to handle this psychologically?",
                "Why do I often have negative thoughts about the future even though my current grades are good?",
                "A sudden loss of interest in old hobbies (listening to music, gaming, drawing) says what?",
                "Why do I constantly compare myself to fake scenarios on social media?",
                "Erratic mood swings from extreme euphoria to deep depression within a single day—what is this a sign of?",
                "The feeling of a vague fear constantly lurking around me everywhere is called what?",
                "Why does receiving compliments from others make me feel ashamed and uncomfortable?",
                "Is the craving to sleep 12-14 hours a day continuously a brain defense mechanism?",
                "Feeling disconnected from close friends even though we chat every day. How to explain this?",
                "Why do I often get the urge to run far away whenever family conflicts peak?",
                "The phenomenon of creating fake arguments in my head and getting mad at myself. What is this?",
                "Guilt over spending my parents' money on personal entertainment reflects what psychology?",
                "Why do I always feel like the victim in every argument?",
                "Is it normal to feel like I have to wear different 'masks' when meeting different groups of people?",
                "Why is my first reaction to any new challenge always wanting to quit?",
                "Craving attention from others, but finding it annoying when I actually get it. What is this?",
                "Frequent headaches or stomach aches at specific times of the week—is this related to stress?",
                "Why am I so quick to forgive others' mistakes but extremely harsh on myself?",
                "Claustrophobia or the fear of absolute silence in the exam room—how to decode this?",
                "Feeling like I'm being watched or judged by everyone around me. Where does this come from?",
                "Why does setting goals make me feel more pressured than not having any goals at all?",
                "Addiction to feeling safe to the point of never daring to try any new experience says what?",
                "A complete loss of faith in the sincerity of the people around me is the result of what?",
                "Why am I often obsessed with minor mistakes I made years ago?",
                "Feeling like I've matured too fast for my age and have to carry too many negative emotions?"
            ],
            'Advice': [
                "I feel like I have no outstanding strengths. How do I escape this inferiority complex?",
                "Lately I'm addicted to social media and scrolling mindlessly for hours. How do I stop?",
                "I'm terrified of being judged. How do I stop caring about what other people think?",
                "I suddenly feel completely lost and don't know where to start organizing my life again.",
                "Every time I fail or make a mistake, I beat myself up for a long time. How to forgive myself?",
                "I always procrastinate until the last minute. How do I build discipline?",
                "I always feel the pressure to be perfect in everyone's eyes. It's exhausting.",
                "How to set boundaries with friends who only come to me to dump their negative energy?",
                "Sometimes I just want to escape reality for a while. How do I overcome this feeling?",
                "Peer pressure is hitting me hard. Everyone is succeeding while I'm stuck. What should I do?",
                "Every time I start something new, I imagine the worst-case scenario. How to be less negative?",
                "My current life feels monotonous and meaningless. How do I find the joy of living again?",
                "When facing difficulties, I tend to withdraw and don't want to ask for help. Is this good?",
                "How to learn to accept things that are beyond my control?",
                "I constantly compare my present self to my past self and feel worse. How to escape this trap?",
                "When everything collapses at once, what should I prioritize fixing first?",
                "How to practice patience when I always want to see immediate results?",
                "I am easily affected by the moods of people around me. How to keep my own calm?",
                "Lately I've fallen into a state of doubting my own self-worth. What advice do I need right now?",
                "How to overcome systemic laziness, not just temporary fatigue?",
                "I set unrealistically high standards and then disappoint myself. How to adjust this?",
                "When I feel like the whole world has turned its back on me, who can I lean on?",
                "How to learn to say no politely without feeling guilty?",
                "I really want to change myself but I'm afraid to step out of my comfort zone. How to gain momentum?",
                "How to maintain kindness and faith in humanity after being betrayed multiple times?",
                "Whenever I face a big decision, I freeze out of fear of choosing wrong. How to handle this?",
                "I always feel like a defective version compared to people's expectations. How to drop this burden?",
                "How to balance being strict with myself and knowing how to comfort myself when tired?",
                "Lately I've lost the ability to listen and get angry easily. How to become calm again?",
                "I want to find a hobby to heal my mental health, but I don't know where to start.",
                "Is there a way to turn jealousy into motivation for self-improvement instead of self-torment?",
                "I feel like I'm living too fast and missing out on beautiful moments. How to slow down?",
                "How to face the fear of loneliness as friends gradually go their separate ways?",
                "I often bottle up my emotions until I explode. Are there healthy ways to release stress?",
                "I feel like I try 200% but my results are still worse than someone who tries 50%. How to not be resentful?",
                "What should I do when I realize the goals I set at the beginning of the year no longer fit?",
                "I want to start journaling to destress, but I give up after a few days. How to maintain it?",
                "I'm often forced into making decisions for others. How do I escape this role?",
                "When my self-belief hits rock bottom, what is the first thing I should do?",
                "How to distinguish between sincere constructive criticism and personal attacks?",
                "I always feel like there's never enough time in a day. How to live more leisurely?",
                "I constantly have to force myself to appear strong and it's exhausting. How to live authentically?",
                "How to cope with the regret over opportunities I missed in the past?",
                "What should I do when I feel the advice from adults is no longer relevant to my reality?",
                "How to create internal motivation instead of relying on external praise or criticism?"
            ]
        },
        'Parent': {
            'Psychology': [
                "What are the common psychological characteristics of a 12th grader preparing for university exams?",
                "Why does my child at this age become withdrawn, share less, and get easily irritated with parents?",
                "How does a 16-18 year old's need for privacy and self-assertion manifest?",
                "How does the fear of failure and disappointing parents affect a teen's exam psychology?",
                "How does covert rebellion in 17-18 year olds show up in daily life?",
                "Why does my child value their friends' opinions more than sincere advice from their parents?",
                "How do FOMO (Fear Of Missing Out) and achievement pressure on social media affect teens?",
                "How does the desire to act like an adult combined with immature emotional control manifest at 18?",
                "How does an identity crisis at 18 affect the way a child chooses their future?"
            ],
            'Behavior': [
                "My child often locks their bedroom door and smashes things when angry. What should I do?",
                "Staying up very late on the phone accompanied by a sudden drop in grades is a sign of what psychological issue?",
                "What does it mean if my child isolates themselves, skips meals, or shows signs of self-harm?",
                "My child frequently lies about their academic results. How should parents understand this behavior?",
                "What does it mean when a teen brushes off or gets angry every time parents ask about their studies/exams?",
                "My 18-year-old suddenly changes clothing styles, dyes their hair bright colors, or gets a tattoo. What does this show?",
                "My teen often complains that 'life is meaningless' or they are 'tired of life'. Are these dangerous warning signs?",
                "What does it mean if my child shows resistance by going completely silent whenever the family brings up exams?",
                "Spending too much time in negative online communities reflects what psychological deficit?",
                "Is it a sign of juvenile delinquency when my teen starts hiding things and lying about their whereabouts after school?",
                "Erratic eating—sometimes bingeing, sometimes constantly skipping meals—is a symptom of what disorder?",
                "What does it warn us of when a child suddenly cleans their room spotlessly and gives away prized possessions?",
                "My child gets startled and hides their phone whenever I walk into the room. What suspicious or secretive psychology does this reflect?",
                "Constantly demanding large sums of money without a clear reason hides what risks?",
                "Starting to use e-cigarettes or stimulants in their private room indicates what kind of desperation?",
                "Frequently complaining of headaches or stomach aches right before going to tutoring classes says what?",
                "Constantly picking at the skin on their hands or pulling out hair until it bleeds—how does this behavior release stress?",
                "Skipping school to play games all night while lying about group studying hides what kind of fear?",
                "Reacting violently and crying hysterically over a very minor parental suggestion shows what about their tolerance threshold?",
                "What does it reflect when a teen refuses to participate in all family trips or family dinners?",
                "Buying a lot of supplements or unknown pills online to take—what does this mean?",
                "Tearing up bad test papers or hiding report cards reflects what kind of pressure?",
                "Starting to have a disrespectful attitude and challenging 'go ahead and hit me' shows what reckless psychology?",
                "Staring blankly into space for hours without doing anything reflects what kind of emptiness?",
                "Constantly changing phone and computer passwords with extreme vigilance?",
                "Scribbling frantically or writing negative words in school notebooks shows what kind of emotional release?",
                "Suddenly cutting off contact with their old close friend group and hanging out with a completely new crowd?",
                "Always intentionally going to sleep very late to avoid facing parents in the evening?",
                "Developing a habit of compulsive shopping on e-commerce platforms even if they don't use the items?",
                "Hiding wrist scars by always wearing long sleeves in the middle of a hot summer?",
                "Getting easily startled, panicked, and breaking into a cold sweat when hearing a phone ring or a knock on the door?",
                "Constantly refusing to eat with the family and demanding to take food to their room to eat alone?",
                "Starting to talk casually about spiritual topics, death, or 'release'?",
                "Hoarding sharp objects (knives, scissors, razor blades) hidden under pillows or in desk drawers?",
                "Reacting with apathy and zero emotion when harshly scolded by parents is a sign of what?",
                "Completely neglecting their major subjects at school to dedicate all their time to a bizarre hobby?",
                "Constantly double-checking door locks and faucets multiple times before bed reflects what kind of anxiety?",
                "Starting to abuse or chase away household pets when stressed?",
                "Deleting all personal posts and photos on social media indicates what psychological desire to disappear?",
                "Skipping official school classes unexcused to wander around coffee shops?",
                "Pulling hair, punching walls, or slapping their own face whenever they can't solve a homework problem?",
                "Constantly looking in the mirror and obsessively complaining about every tiny physical flaw?",
                "Starting to follow websites with violent content, suicide, or deviant ideologies?",
                "Acting extremely obedient in a robotic way, but their eyes are completely lifeless and devoid of energy?",
                "Intentionally breaking expensive items that parents just bought for them to prove what point?",
                "Talking to themselves in a closed room or displaying bizarre mannerisms when stressed?",
                "Absolutely never mentioning classmates' names or school stories after coming home?",
                "Showing signs of gathering and hiding various medications in a separate box at home?"
            ],
            'Understanding': [
                "How to start a conversation when my child is constantly defensive and withdrawn?",
                "How should I ask questions so my child feels safe, unjudged, and willing to share with me?",
                "How to balance closely monitoring my child's studies and respecting their right to privacy?",
                "How to recognize if my child is facing severe pressure at school but refuses to talk about it?",
                "What attitude should parents adopt when their child gets bad mock exam results to avoid hurting them further?",
                "How can parents learn to accept that their child's dreams are completely different from their expectations?",
                "How to make my child feel that home is the safest place to return to whenever they experience failure?",
                "What is the right way to praise and encourage an 18-year-old without causing the opposite effect or adding pressure?",
                "How can parents maintain their calm and not get angry when their child intentionally says provoking things?"
            ],
            'Action': [
                "What should I do immediately upon discovering my child shows signs of extreme stress, anxiety, or depression?",
                "When seeing my child distracted from their studies by puppy love, how should parents handle it delicately?",
                "How should parents prepare and act to help their child reduce pressure for the upcoming decisive exams?",
                "How should I react if my child comes out about their sexual orientation to the family?",
                "What should parents do when a child firmly chooses a college major that the family knows will be very difficult for a future career?",
                "How to handle the situation upon discovering my child is being bullied by a group or psychologically manipulated at school?",
                "How should parents act when their child shows signs of panic attacks right before exam day?",
                "How should parents intervene when their teen is so addicted to gaming or idolizing celebrities that they neglect exams?",
                "What must I do if my child outright refuses to see a psychologist even though they are in a very bad state?",
                "How should parents handle discovering their child is using stimulants or e-cigarettes?"
            ]
        }
    }
}
