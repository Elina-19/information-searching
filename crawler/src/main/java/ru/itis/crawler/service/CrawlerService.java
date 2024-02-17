package ru.itis.crawler.service;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.eclipse.microprofile.faulttolerance.Fallback;
import org.eclipse.microprofile.faulttolerance.Retry;
import org.jsoup.Jsoup;
import ru.itis.crawler.dto.DocumentDTO;
import ru.itis.crawler.dto.FileDTO;
import ru.itis.crawler.exception.DownloadDocumentException;

import javax.enterprise.context.ApplicationScoped;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;

@ApplicationScoped
@Slf4j
public class CrawlerService {

    private final String STORAGE_PATH = "C:\\Users\\Repositories\\itis\\information-searching\\crawler\\storage\\";
    private final String REPORT_NAME = "index.txt";

    public FileDTO download(FileDTO fileDTO) {
        var links = getLinks(fileDTO);
        var documentDTOS = links.parallelStream()
                .map(this::download)
                .filter(Objects::nonNull)
                .map(this::save)
                .collect(Collectors.toList());
        return getReport(documentDTOS);
    }

    private List<String> getLinks(FileDTO fileDTO) {
        List<String> links = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(new ByteArrayInputStream(fileDTO.getFile()), StandardCharsets.UTF_8))) {
            var line = br.readLine();
            while (line != null) {
                links.add(line);
                line = br.readLine();
            }
            return links;
        } catch (IOException e) {
            log.error("Can not read links from file: ", e);
            return Collections.emptyList();
        }
    }

    // @Retry позволяет автоматически запускать метод повторно при возникновении исключения DownloadDocumentException
    // По умолчанию количество попыток 3, после 3 fail-ов вызывается fallback метод
    @Retry(retryOn = DownloadDocumentException.class)
    @Fallback(fallbackMethod = "fallback")
    public DocumentDTO download(String url) {
        try {
            log.info("Get page {}", url);
            return DocumentDTO.builder()
                    .url(url)
                    .document(Jsoup.connect(url).get())
                    .build();
        } catch (IOException e) {
            log.error("Error when get content from url: {}", url, e);
            throw new DownloadDocumentException();
        }
    }

    public DocumentDTO fallback(String url) {
        log.info("Failed load document from url: {}", url);
        return null;
    }

    private DocumentDTO save(DocumentDTO documentDTO) {
        var fileName  = UUID.randomUUID().toString();
        var file = new File(STORAGE_PATH + fileName + ".html");
        try {
            FileUtils.writeStringToFile(file, documentDTO.getDocument().toString(), StandardCharsets.UTF_8);
            documentDTO.setId(fileName);
            return documentDTO;
        } catch (IOException e) {
            log.error("Failed save {}", documentDTO.getUrl());
            return documentDTO;
        }
    }

    private FileDTO getReport(List<DocumentDTO> documentDTOS) {
        var report = FileDTO.builder()
                .name(REPORT_NAME)
                .build();
        try (ByteArrayOutputStream os = new ByteArrayOutputStream()) {
            for (var d: documentDTOS) {
                os.write((d.getId() + " " + d.getUrl() + "\n").getBytes(StandardCharsets.UTF_8));
            }
            report.setFile(os.toByteArray());
            return report;
        } catch (IOException e) {
            log.error("Failed make report");
            return report;
        }
    }
}
