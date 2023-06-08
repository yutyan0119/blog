# require 'open-uri'
# require 'json'
# require 'nokogiri'

# module Jekyll
#   class OgpEnrichment < Generator
#     safe true
#     priority :low

#     def generate(site)
#       site.pages.each { |page| process_page(page) }
#       site.posts.docs.each { |post| process_page(post) }
#     end

#     def process_page(page)
#       # return if !page.content.strip.start_with?("<!DOCTYPE")
#       doc = Nokogiri::HTML(page.content)

#       doc.css('a').each do |link|
#         url = link['href']

#         if url == link.content
#           ogp_info = fetch_ogp_info(url)

#           if ogp_info
#             link.replace(build_link_with_ogp(link, ogp_info))
#           end
#         end
#       end

#       page.content = doc.to_html
#     end

#     def build_link_with_ogp(link, ogp_info)
#       <<-HTML
#       <a href="#{ogp_info['url']}">
#         <div class="ogp-container">
#           <img src="#{ogp_info['images'][0]}" />
#           <div>#{ogp_info['title']}</div>
#         </div>
#       </a>
#       HTML
#     end

#     def fetch_ogp_info(url)
#       ogp_info_url = "https://jsonlink.io/api/extract?url=#{URI.escape(url)}"
#       response = URI.open(ogp_info_url)
#       JSON.parse(response.read)
#     rescue
#       puts "Error fetching OGP info for #{url}"
#       nil
#     end
#   end
# end
